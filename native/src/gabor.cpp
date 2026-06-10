#include <complex>

#include "common.hpp"

namespace tsdecomp_native {

namespace {

using Complex = std::complex<double>;

bool is_power_of_two(std::size_t n) {
    return n > 0 && (n & (n - 1)) == 0;
}

void fft_inplace(std::vector<Complex>& a, bool inverse) {
    const std::size_t n = a.size();
    for (std::size_t i = 1, j = 0; i < n; ++i) {
        std::size_t bit = n >> 1;
        for (; j & bit; bit >>= 1) {
            j ^= bit;
        }
        j ^= bit;
        if (i < j) {
            std::swap(a[i], a[j]);
        }
    }

    for (std::size_t len = 2; len <= n; len <<= 1) {
        const double angle = 2.0 * kPi / static_cast<double>(len) * (inverse ? 1.0 : -1.0);
        const Complex wlen(std::cos(angle), std::sin(angle));
        for (std::size_t i = 0; i < n; i += len) {
            Complex w(1.0, 0.0);
            for (std::size_t j = 0; j < len / 2; ++j) {
                const Complex u = a[i + j];
                const Complex v = a[i + j + len / 2] * w;
                a[i + j] = u + v;
                a[i + j + len / 2] = u - v;
                w *= wlen;
            }
        }
    }

    if (inverse) {
        const double scale = 1.0 / static_cast<double>(n);
        for (auto& value : a) {
            value *= scale;
        }
    }
}

std::vector<Complex> dft(const std::vector<Complex>& x, bool inverse) {
    const std::size_t n = x.size();
    std::vector<Complex> out(n, Complex(0.0, 0.0));
    const double sign = inverse ? 1.0 : -1.0;
    for (std::size_t k = 0; k < n; ++k) {
        Complex acc(0.0, 0.0);
        for (std::size_t t = 0; t < n; ++t) {
            const double angle =
                sign * 2.0 * kPi * static_cast<double>(k) * static_cast<double>(t) / static_cast<double>(n);
            acc += x[t] * Complex(std::cos(angle), std::sin(angle));
        }
        out[k] = inverse ? acc / static_cast<double>(n) : acc;
    }
    return out;
}

std::vector<Complex> transform(std::vector<Complex> x, bool inverse) {
    if (is_power_of_two(x.size())) {
        fft_inplace(x, inverse);
        return x;
    }
    return dft(x, inverse);
}

std::vector<double> as_window_vector(
    const py::array_t<double, py::array::c_style | py::array::forcecast>& arr,
    int expected) {
    if (arr.ndim() != 1) {
        throw std::invalid_argument("Gabor window must be 1D.");
    }
    if (arr.shape(0) != expected) {
        throw std::invalid_argument("Gabor window length must match win_len.");
    }
    auto view = arr.unchecked<1>();
    std::vector<double> out(static_cast<std::size_t>(expected), 0.0);
    for (int i = 0; i < expected; ++i) {
        out[static_cast<std::size_t>(i)] = view(i);
    }
    return out;
}

}  // namespace

py::array_t<std::complex<float>> gabor_stft_rfft(
    const py::array_t<double, py::array::c_style | py::array::forcecast>& x_arr,
    int win_len,
    int hop,
    int n_fft,
    const py::array_t<double, py::array::c_style | py::array::forcecast>& window_arr) {
    auto x = as_vector(x_arr);
    if (win_len <= 0 || hop <= 0 || n_fft < win_len) {
        throw std::invalid_argument("Gabor STFT requires win_len > 0, hop > 0, and n_fft >= win_len.");
    }
    const auto window = as_window_vector(window_arr, win_len);
    const std::size_t N = x.size();
    const std::size_t L = static_cast<std::size_t>(win_len);
    const std::size_t H = static_cast<std::size_t>(hop);
    const std::size_t F = static_cast<std::size_t>(n_fft);
    const std::size_t frames = N < L ? 1 : 1 + (N - L) / H;
    const std::size_t bins = F / 2 + 1;

    auto out = py::array_t<std::complex<float>>({
        static_cast<py::ssize_t>(frames),
        static_cast<py::ssize_t>(bins),
    });
    auto view = out.mutable_unchecked<2>();

    for (std::size_t frame = 0; frame < frames; ++frame) {
        const std::size_t start = frame * H;
        std::vector<Complex> buffer(F, Complex(0.0, 0.0));
        for (std::size_t i = 0; i < L; ++i) {
            const std::size_t idx = start + i;
            const double sample = idx < N ? x[idx] : 0.0;
            buffer[i] = Complex(sample * window[i], 0.0);
        }
        auto spectrum = transform(std::move(buffer), false);
        for (std::size_t bin = 0; bin < bins; ++bin) {
            view(static_cast<py::ssize_t>(frame), static_cast<py::ssize_t>(bin)) =
                std::complex<float>(static_cast<float>(spectrum[bin].real()), static_cast<float>(spectrum[bin].imag()));
        }
    }
    return out;
}

py::array_t<double> gabor_istft_rfft(
    const py::array_t<std::complex<float>, py::array::c_style | py::array::forcecast>& Z_arr,
    int win_len,
    int hop,
    int n_fft,
    const py::array_t<double, py::array::c_style | py::array::forcecast>& window_arr,
    int length) {
    if (Z_arr.ndim() != 2) {
        throw std::invalid_argument("Gabor ISTFT spectrum must be 2D.");
    }
    if (win_len <= 0 || hop <= 0 || n_fft < win_len || length < 0) {
        throw std::invalid_argument("Gabor ISTFT requires valid win_len, hop, n_fft, and length.");
    }
    const auto window = as_window_vector(window_arr, win_len);
    const std::size_t frames = static_cast<std::size_t>(Z_arr.shape(0));
    const std::size_t bins = static_cast<std::size_t>(Z_arr.shape(1));
    const std::size_t L = static_cast<std::size_t>(win_len);
    const std::size_t H = static_cast<std::size_t>(hop);
    const std::size_t F = static_cast<std::size_t>(n_fft);
    if (bins != F / 2 + 1) {
        throw std::invalid_argument("Gabor ISTFT spectrum bin count must equal n_fft / 2 + 1.");
    }

    const std::size_t out_len = static_cast<std::size_t>(length) + L;
    std::vector<double> x_rec(out_len, 0.0);
    std::vector<double> win_acc(out_len, 0.0);
    auto view = Z_arr.unchecked<2>();

    for (std::size_t frame = 0; frame < frames; ++frame) {
        std::vector<Complex> spectrum(F, Complex(0.0, 0.0));
        for (std::size_t bin = 0; bin < bins; ++bin) {
            const auto value = view(static_cast<py::ssize_t>(frame), static_cast<py::ssize_t>(bin));
            spectrum[bin] = Complex(static_cast<double>(value.real()), static_cast<double>(value.imag()));
        }
        for (std::size_t bin = 1; bin + 1 < bins; ++bin) {
            spectrum[F - bin] = std::conj(spectrum[bin]);
        }
        auto time = transform(std::move(spectrum), true);
        const std::size_t start = frame * H;
        for (std::size_t i = 0; i < L && start + i < out_len; ++i) {
            x_rec[start + i] += time[i].real() * window[i];
            win_acc[start + i] += window[i] * window[i];
        }
    }

    std::vector<double> out_values(static_cast<std::size_t>(length), 0.0);
    for (std::size_t i = 0; i < out_values.size(); ++i) {
        if (win_acc[i] > 1e-12) {
            out_values[i] = x_rec[i] / win_acc[i];
        }
    }
    return to_numpy(out_values);
}

py::dict gabor_cluster_decompose(
    const py::array_t<double, py::array::c_style | py::array::forcecast>& x_arr,
    const py::array_t<float, py::array::c_style | py::array::forcecast>& centroids_arr,
    const py::array_t<float, py::array::c_style | py::array::forcecast>& mu_arr,
    const py::array_t<float, py::array::c_style | py::array::forcecast>& sigma_arr,
    int win_len,
    int hop,
    int n_fft,
    const py::array_t<double, py::array::c_style | py::array::forcecast>& window_arr,
    bool use_log_amp,
    int max_clusters,
    double trend_freq_thr) {
    auto x = as_vector(x_arr);
    if (centroids_arr.ndim() != 2 || centroids_arr.shape(1) != 3) {
        throw std::invalid_argument("Gabor centroids must have shape (n_clusters, 3).");
    }
    if (mu_arr.ndim() != 1 || sigma_arr.ndim() != 1 || mu_arr.shape(0) != 3 || sigma_arr.shape(0) != 3) {
        throw std::invalid_argument("Gabor mu and sigma must have shape (3,).");
    }
    const std::size_t K = static_cast<std::size_t>(centroids_arr.shape(0));
    if (K == 0) {
        throw std::invalid_argument("Gabor model must contain at least one centroid.");
    }

    auto centroids = centroids_arr.unchecked<2>();
    auto mu = mu_arr.unchecked<1>();
    auto sigma = sigma_arr.unchecked<1>();

    py::array_t<std::complex<float>> Z = gabor_stft_rfft(x_arr, win_len, hop, n_fft, window_arr);
    auto z_view = Z.unchecked<2>();
    const std::size_t frames = static_cast<std::size_t>(Z.shape(0));
    const std::size_t bins = static_cast<std::size_t>(Z.shape(1));
    const std::size_t atoms = frames * bins;

    std::vector<int> labels(atoms, 0);
    std::vector<double> energy_per_cluster(K, 0.0);
    for (std::size_t frame = 0; frame < frames; ++frame) {
        const float t_norm = frames > 1 ? static_cast<float>(frame) / static_cast<float>(frames - 1) : 0.0f;
        for (std::size_t bin = 0; bin < bins; ++bin) {
            const auto value = z_view(static_cast<py::ssize_t>(frame), static_cast<py::ssize_t>(bin));
            const float amp = std::abs(value);
            const float amp_feat = use_log_amp ? std::log1p(amp) : amp;
            const float f_norm = bins > 1 ? static_cast<float>(bin) / static_cast<float>(bins - 1) : 0.0f;
            float feat[3] = {t_norm, f_norm, amp_feat};
            for (int dim = 0; dim < 3; ++dim) {
                const float denom = std::abs(sigma(dim)) > 1e-12f ? sigma(dim) : 1.0f;
                feat[dim] = (feat[dim] - mu(dim)) / denom;
            }

            int best = 0;
            double best_dist = std::numeric_limits<double>::infinity();
            for (std::size_t cluster = 0; cluster < K; ++cluster) {
                double dist = 0.0;
                for (int dim = 0; dim < 3; ++dim) {
                    const double delta = static_cast<double>(feat[dim] - centroids(static_cast<py::ssize_t>(cluster), dim));
                    dist += delta * delta;
                }
                if (dist < best_dist) {
                    best_dist = dist;
                    best = static_cast<int>(cluster);
                }
            }

            const std::size_t atom_idx = frame * bins + bin;
            labels[atom_idx] = best;
            energy_per_cluster[static_cast<std::size_t>(best)] += static_cast<double>(amp) * static_cast<double>(amp);
        }
    }

    std::vector<bool> keep_mask(K, true);
    if (max_clusters >= 0 && static_cast<std::size_t>(max_clusters) < K) {
        std::fill(keep_mask.begin(), keep_mask.end(), false);
        std::vector<std::size_t> order(K);
        std::iota(order.begin(), order.end(), 0);
        std::sort(order.begin(), order.end(), [&](std::size_t a, std::size_t b) {
            return energy_per_cluster[a] > energy_per_cluster[b];
        });
        for (int i = 0; i < max_clusters; ++i) {
            keep_mask[order[static_cast<std::size_t>(i)]] = true;
        }
    }

    const std::size_t N = x.size();
    py::dict components;
    py::list used_clusters;
    std::vector<double> trend(N, 0.0);
    std::vector<double> season(N, 0.0);
    std::vector<double> sum_comp(N, 0.0);

    for (std::size_t cluster = 0; cluster < K; ++cluster) {
        if (!keep_mask[cluster]) {
            continue;
        }
        bool any = false;
        auto Zj = py::array_t<std::complex<float>>({
            static_cast<py::ssize_t>(frames),
            static_cast<py::ssize_t>(bins),
        });
        auto zj_view = Zj.mutable_unchecked<2>();
        for (std::size_t frame = 0; frame < frames; ++frame) {
            for (std::size_t bin = 0; bin < bins; ++bin) {
                const std::size_t atom_idx = frame * bins + bin;
                if (labels[atom_idx] == static_cast<int>(cluster)) {
                    zj_view(static_cast<py::ssize_t>(frame), static_cast<py::ssize_t>(bin)) =
                        z_view(static_cast<py::ssize_t>(frame), static_cast<py::ssize_t>(bin));
                    any = true;
                } else {
                    zj_view(static_cast<py::ssize_t>(frame), static_cast<py::ssize_t>(bin)) =
                        std::complex<float>(0.0f, 0.0f);
                }
            }
        }
        if (!any) {
            continue;
        }

        py::array_t<double> component = gabor_istft_rfft(Zj, win_len, hop, n_fft, window_arr, static_cast<int>(N));
        auto comp_view = component.unchecked<1>();
        const bool is_trend = centroids(static_cast<py::ssize_t>(cluster), 1) <= trend_freq_thr;
        for (std::size_t i = 0; i < N; ++i) {
            const double value = comp_view(static_cast<py::ssize_t>(i));
            sum_comp[i] += value;
            if (is_trend) {
                trend[i] += value;
            } else {
                season[i] += value;
            }
        }
        components[py::str("Cluster_" + std::to_string(cluster))] = component;
        used_clusters.append(static_cast<int>(cluster));
    }

    std::vector<double> residual(N, 0.0);
    for (std::size_t i = 0; i < N; ++i) {
        residual[i] = x[i] - sum_comp[i];
    }

    py::dict meta;
    meta["method"] = "GABOR_CLUSTER_NATIVE";
    meta["n_clusters"] = static_cast<int>(K);
    meta["used_clusters"] = used_clusters;
    if (max_clusters >= 0) {
        meta["max_clusters"] = max_clusters;
    } else {
        meta["max_clusters"] = py::none();
    }

    py::dict out;
    out["trend"] = to_numpy(trend);
    out["season"] = to_numpy(season);
    out["residual"] = to_numpy(residual);
    out["components"] = components;
    out["meta"] = meta;
    return out;
}

}  // namespace tsdecomp_native
