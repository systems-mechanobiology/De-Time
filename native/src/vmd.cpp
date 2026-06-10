#include <complex>

#include "common.hpp"

namespace tsdecomp_native {

namespace {

using Complex = std::complex<double>;

std::vector<Complex> to_complex_vector(const py::object& obj) {
    auto arr = obj.cast<py::array_t<Complex, py::array::c_style | py::array::forcecast>>();
    if (arr.ndim() != 1) {
        throw std::invalid_argument("Expected a 1D complex array.");
    }
    auto view = arr.unchecked<1>();
    std::vector<Complex> out(static_cast<std::size_t>(view.shape(0)));
    for (std::size_t i = 0; i < out.size(); ++i) {
        out[i] = view(static_cast<py::ssize_t>(i));
    }
    return out;
}

py::array_t<Complex> to_numpy_complex(const std::vector<Complex>& values) {
    auto out = py::array_t<Complex>(values.size());
    auto view = out.mutable_unchecked<1>();
    for (std::size_t i = 0; i < values.size(); ++i) {
        view(static_cast<py::ssize_t>(i)) = values[i];
    }
    return out;
}

py::array_t<double> to_numpy_modes(
    const std::vector<double>& values,
    std::size_t modes,
    std::size_t length) {
    auto out = py::array_t<double>({
        static_cast<py::ssize_t>(modes),
        static_cast<py::ssize_t>(length),
    });
    auto view = out.mutable_unchecked<2>();
    for (std::size_t k = 0; k < modes; ++k) {
        const std::size_t base = k * length;
        for (std::size_t t = 0; t < length; ++t) {
            view(static_cast<py::ssize_t>(k), static_cast<py::ssize_t>(t)) = values[base + t];
        }
    }
    return out;
}

py::array_t<double> to_numpy_omega(const std::vector<double>& values) {
    auto out = py::array_t<double>({static_cast<py::ssize_t>(1), static_cast<py::ssize_t>(values.size())});
    auto view = out.mutable_unchecked<2>();
    for (std::size_t k = 0; k < values.size(); ++k) {
        view(0, static_cast<py::ssize_t>(k)) = values[k];
    }
    return out;
}

std::vector<Complex> fftshift_even(const std::vector<Complex>& x) {
    const std::size_t n = x.size();
    std::vector<Complex> out(n);
    const std::size_t half = n / 2;
    for (std::size_t i = 0; i < n; ++i) {
        out[i] = x[(i + half) % n];
    }
    return out;
}

std::vector<Complex> ifftshift_even(const std::vector<Complex>& x) {
    return fftshift_even(x);
}

std::vector<Complex> numpy_fft(const std::vector<double>& x) {
    py::module_ np_fft = py::module_::import("numpy.fft");
    return to_complex_vector(np_fft.attr("fft")(to_numpy(x)));
}

std::vector<Complex> numpy_ifft(const std::vector<Complex>& x) {
    py::module_ np_fft = py::module_::import("numpy.fft");
    return to_complex_vector(np_fft.attr("ifft")(to_numpy_complex(x)));
}

std::vector<double> mirror_signal_even(const std::vector<double>& input) {
    std::vector<double> f = input;
    if (f.size() % 2 == 1) {
        f.pop_back();
    }
    const std::size_t n = f.size();
    const std::size_t half = n / 2;
    std::vector<double> out;
    out.reserve(2 * n);
    for (std::size_t i = 0; i < half; ++i) {
        out.push_back(f[half - 1 - i]);
    }
    out.insert(out.end(), f.begin(), f.end());
    for (std::size_t i = 0; i < half; ++i) {
        out.push_back(f[n - 1 - i]);
    }
    return out;
}

double weighted_center_frequency(
    const std::vector<Complex>& spectrum,
    const std::vector<double>& freqs,
    std::size_t start) {
    double numerator = 0.0;
    double denominator = 0.0;
    for (std::size_t i = start; i < spectrum.size(); ++i) {
        const double power = std::norm(spectrum[i]);
        numerator += freqs[i] * power;
        denominator += power;
    }
    if (denominator <= 1e-24 || !std::isfinite(denominator)) {
        return 0.0;
    }
    return numerator / denominator;
}

double update_difference(
    const std::vector<std::vector<Complex>>& current,
    const std::vector<std::vector<Complex>>& previous,
    std::size_t T) {
    double acc = std::numeric_limits<double>::epsilon();
    for (std::size_t k = 0; k < current.size(); ++k) {
        for (std::size_t i = 0; i < current[k].size(); ++i) {
            acc += std::norm(current[k][i] - previous[k][i]) / static_cast<double>(T);
        }
    }
    return std::abs(acc);
}

std::vector<double> reconstruct_modes(
    const std::vector<std::vector<Complex>>& u_hat_plus,
    std::size_t original_length) {
    const std::size_t K = u_hat_plus.size();
    const std::size_t T = K == 0 ? 0 : u_hat_plus[0].size();
    std::vector<double> modes(K * original_length, 0.0);
    for (std::size_t k = 0; k < K; ++k) {
        std::vector<Complex> u_hat(T, Complex(0.0, 0.0));
        for (std::size_t i = T / 2; i < T; ++i) {
            u_hat[i] = u_hat_plus[k][i];
        }
        for (std::size_t offset = 0; offset < T / 2; ++offset) {
            const std::size_t idx = T / 2 - offset;
            u_hat[idx] = std::conj(u_hat_plus[k][T / 2 + offset]);
        }
        if (T > 0) {
            u_hat[0] = std::conj(u_hat[T - 1]);
        }

        auto time = numpy_ifft(ifftshift_even(u_hat));
        const std::size_t start = T / 4;
        for (std::size_t t = 0; t < original_length; ++t) {
            modes[k * original_length + t] = time[start + t].real();
        }
    }
    return modes;
}

}  // namespace

py::dict vmd_decompose(
    const py::array_t<double, py::array::c_style | py::array::forcecast>& y_arr,
    double alpha,
    double tau,
    int K_raw,
    int DC,
    int init,
    double tol,
    int max_iter,
    unsigned int seed) {
    auto input = as_vector(y_arr);
    if (input.size() < 4) {
        throw std::invalid_argument("VMD requires series length >= 4.");
    }
    if (input.size() % 2 == 1) {
        input.pop_back();
    }
    const std::size_t original_length = input.size();
    const int K_int = std::max(1, K_raw);
    const std::size_t K = static_cast<std::size_t>(K_int);
    const std::size_t Niter = static_cast<std::size_t>(std::max(2, max_iter));

    auto mirrored = mirror_signal_even(input);
    const std::size_t T = mirrored.size();
    const std::size_t half = T / 2;
    std::vector<double> freqs(T, 0.0);
    for (std::size_t i = 0; i < T; ++i) {
        freqs[i] = static_cast<double>(i) / static_cast<double>(T) - 0.5;
    }

    auto f_hat = fftshift_even(numpy_fft(mirrored));
    std::vector<Complex> f_hat_plus = f_hat;
    for (std::size_t i = 0; i < half; ++i) {
        f_hat_plus[i] = Complex(0.0, 0.0);
    }

    std::vector<double> omega(K, 0.0);
    std::vector<double> omega_next(K, 0.0);
    if (init == 1) {
        for (std::size_t k = 0; k < K; ++k) {
            omega[k] = 0.5 * static_cast<double>(k) / static_cast<double>(K);
        }
    } else if (init == 2) {
        std::mt19937 rng(seed);
        std::uniform_real_distribution<double> uniform(0.0, 1.0);
        const double fs = 1.0 / static_cast<double>(original_length);
        for (std::size_t k = 0; k < K; ++k) {
            omega[k] = std::exp(std::log(fs) + (std::log(0.5) - std::log(fs)) * uniform(rng));
        }
        std::sort(omega.begin(), omega.end());
    }
    if (DC && !omega.empty()) {
        omega[0] = 0.0;
    }

    std::vector<std::vector<Complex>> previous(K, std::vector<Complex>(T, Complex(0.0, 0.0)));
    std::vector<std::vector<Complex>> current(K, std::vector<Complex>(T, Complex(0.0, 0.0)));
    std::vector<Complex> lambda(T, Complex(0.0, 0.0));
    std::vector<Complex> lambda_next(T, Complex(0.0, 0.0));
    std::vector<Complex> sum_uk(T, Complex(0.0, 0.0));

    double u_diff = tol + std::numeric_limits<double>::epsilon();
    std::size_t iterations = 0;
    while (u_diff > tol && iterations < Niter - 1) {
        std::size_t k = 0;
        for (std::size_t i = 0; i < T; ++i) {
            sum_uk[i] = previous[K - 1][i] + sum_uk[i] - previous[0][i];
            const double denom = 1.0 + alpha * std::pow(freqs[i] - omega[0], 2.0);
            current[0][i] = (f_hat_plus[i] - sum_uk[i] - lambda[i] / 2.0) / denom;
        }
        omega_next[0] = DC ? 0.0 : weighted_center_frequency(current[0], freqs, half);

        for (k = 1; k < K; ++k) {
            for (std::size_t i = 0; i < T; ++i) {
                sum_uk[i] = current[k - 1][i] + sum_uk[i] - previous[k][i];
                const double denom = 1.0 + alpha * std::pow(freqs[i] - omega[k], 2.0);
                current[k][i] = (f_hat_plus[i] - sum_uk[i] - lambda[i] / 2.0) / denom;
            }
            omega_next[k] = weighted_center_frequency(current[k], freqs, half);
        }

        for (std::size_t i = 0; i < T; ++i) {
            Complex mode_sum(0.0, 0.0);
            for (std::size_t mode = 0; mode < K; ++mode) {
                mode_sum += current[mode][i];
            }
            lambda_next[i] = lambda[i] + tau * (mode_sum - f_hat_plus[i]);
        }

        ++iterations;
        u_diff = update_difference(current, previous, T);
        previous.swap(current);
        for (auto& row : current) {
            std::fill(row.begin(), row.end(), Complex(0.0, 0.0));
        }
        lambda.swap(lambda_next);
        std::fill(lambda_next.begin(), lambda_next.end(), Complex(0.0, 0.0));
        omega.swap(omega_next);
    }

    auto modes = reconstruct_modes(previous, original_length);

    py::dict components;
    components["modes"] = to_numpy_modes(modes, K, original_length);

    py::dict meta;
    meta["method"] = "VMD_NATIVE";
    meta["iterations"] = static_cast<int>(iterations);
    meta["omega"] = omega;

    py::dict out;
    out["modes"] = to_numpy_modes(modes, K, original_length);
    out["omega"] = to_numpy_omega(omega);
    out["components"] = std::move(components);
    out["meta"] = std::move(meta);
    return out;
}

}  // namespace tsdecomp_native
