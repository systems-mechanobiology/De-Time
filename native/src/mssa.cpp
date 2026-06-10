#include "common.hpp"

namespace tsdecomp_native {

namespace {

py::array_t<double> to_numpy_matrix(
    const std::vector<double>& values,
    std::size_t rows,
    std::size_t cols) {
    auto out = py::array_t<double>({static_cast<py::ssize_t>(rows), static_cast<py::ssize_t>(cols)});
    auto view = out.mutable_unchecked<2>();
    for (std::size_t i = 0; i < rows; ++i) {
        const std::size_t base = i * cols;
        for (std::size_t j = 0; j < cols; ++j) {
            view(static_cast<py::ssize_t>(i), static_cast<py::ssize_t>(j)) = values[base + j];
        }
    }
    return out;
}

py::array_t<double> to_numpy_matrix_2d(
    const std::vector<double>& values,
    std::size_t rows,
    std::size_t cols) {
    return to_numpy_matrix(values, rows, cols);
}

py::array_t<double> to_numpy_modes(
    const std::vector<double>& values,
    std::size_t modes,
    std::size_t length,
    std::size_t channels) {
    auto out = py::array_t<double>({
        static_cast<py::ssize_t>(modes),
        static_cast<py::ssize_t>(length),
        static_cast<py::ssize_t>(channels),
    });
    auto view = out.mutable_unchecked<3>();
    for (std::size_t m = 0; m < modes; ++m) {
        const std::size_t mode_base = m * length * channels;
        for (std::size_t t = 0; t < length; ++t) {
            const std::size_t row_base = mode_base + t * channels;
            for (std::size_t c = 0; c < channels; ++c) {
                view(
                    static_cast<py::ssize_t>(m),
                    static_cast<py::ssize_t>(t),
                    static_cast<py::ssize_t>(c)) = values[row_base + c];
            }
        }
    }
    return out;
}

std::vector<double> as_matrix_vector(
    const py::array_t<double, py::array::c_style | py::array::forcecast>& arr,
    std::size_t& rows,
    std::size_t& cols) {
    if (arr.ndim() != 2) {
        throw std::invalid_argument("MSSA native input must be a 2D float64 array.");
    }
    rows = static_cast<std::size_t>(arr.shape(0));
    cols = static_cast<std::size_t>(arr.shape(1));
    std::vector<double> out(rows * cols, 0.0);
    auto view = arr.unchecked<2>();
    for (std::size_t i = 0; i < rows; ++i) {
        for (std::size_t j = 0; j < cols; ++j) {
            out[i * cols + j] = view(static_cast<py::ssize_t>(i), static_cast<py::ssize_t>(j));
        }
    }
    return out;
}

std::vector<double> build_mssa_trajectory_matrix(
    const std::vector<double>& y,
    std::size_t length,
    std::size_t channels,
    std::size_t window,
    std::size_t k) {
    std::vector<double> X(window * channels * k, 0.0);
    for (std::size_t channel = 0; channel < channels; ++channel) {
        const std::size_t row_offset = channel * window;
        for (std::size_t col = 0; col < k; ++col) {
            for (std::size_t row = 0; row < window; ++row) {
                X[(row_offset + row) * k + col] = y[(col + row) * channels + channel];
            }
        }
    }
    return X;
}

std::vector<double> trajectory_matvec(
    const std::vector<double>& X,
    std::size_t rows,
    std::size_t cols,
    const std::vector<double>& v) {
    std::vector<double> out(rows, 0.0);
    for (std::size_t i = 0; i < rows; ++i) {
        const std::size_t base = i * cols;
        double acc = 0.0;
        for (std::size_t j = 0; j < cols; ++j) {
            acc += X[base + j] * v[j];
        }
        out[i] = acc;
    }
    return out;
}

std::vector<double> trajectory_t_matvec(
    const std::vector<double>& X,
    std::size_t rows,
    std::size_t cols,
    const std::vector<double>& u) {
    std::vector<double> out(cols, 0.0);
    for (std::size_t i = 0; i < rows; ++i) {
        const std::size_t base = i * cols;
        for (std::size_t j = 0; j < cols; ++j) {
            out[j] += X[base + j] * u[i];
        }
    }
    return out;
}

void stabilize_component_sign(
    std::vector<double>& u,
    std::vector<double>& v) {
    std::size_t pivot = 0;
    double max_abs = 0.0;
    for (std::size_t i = 0; i < u.size(); ++i) {
        const double candidate = std::abs(u[i]);
        if (candidate > max_abs) {
            max_abs = candidate;
            pivot = i;
        }
    }
    if (!u.empty() && u[pivot] < 0.0) {
        for (double& value : u) {
            value = -value;
        }
        for (double& value : v) {
            value = -value;
        }
    }
}

void diagonal_average_rank1_into_mode(
    const std::vector<double>& u_segment,
    const std::vector<double>& v,
    double sigma,
    std::size_t length,
    std::size_t channel,
    std::size_t channels,
    std::vector<double>& mode_out) {
    const std::size_t rows = u_segment.size();
    const std::size_t cols = v.size();
    std::vector<double> recon(length, 0.0);
    std::vector<double> counts(length, 0.0);
    for (std::size_t i = 0; i < rows; ++i) {
        for (std::size_t j = 0; j < cols; ++j) {
            const std::size_t idx = i + j;
            recon[idx] += sigma * u_segment[i] * v[j];
            counts[idx] += 1.0;
        }
    }
    for (std::size_t t = 0; t < length; ++t) {
        if (counts[t] > 0.0) {
            recon[t] /= counts[t];
        }
        mode_out[t * channels + channel] = recon[t];
    }
}

struct ComponentBasis {
    std::vector<double> modes;
    std::vector<double> singular_values;
    std::size_t mode_count = 0;
};

ComponentBasis compute_mssa_components_exact(
    const std::vector<double>& X,
    std::size_t rows,
    std::size_t k,
    std::size_t rank,
    std::size_t length,
    std::size_t channels,
    std::size_t window) {
    py::module_ np_linalg = py::module_::import("numpy.linalg");
    py::tuple svd = np_linalg.attr("svd")(to_numpy_matrix(X, rows, k), py::arg("full_matrices") = false);
    auto U = svd[0].cast<py::array_t<double, py::array::c_style | py::array::forcecast>>();
    auto singular = svd[1].cast<py::array_t<double, py::array::c_style | py::array::forcecast>>();
    auto Vt = svd[2].cast<py::array_t<double, py::array::c_style | py::array::forcecast>>();

    auto u_view = U.unchecked<2>();
    auto s_view = singular.unchecked<1>();
    auto vt_view = Vt.unchecked<2>();

    const std::size_t upper = std::min<std::size_t>(rank, static_cast<std::size_t>(s_view.shape(0)));
    std::vector<double> modes;
    std::vector<double> singular_values;
    modes.reserve(upper * length * channels);
    singular_values.reserve(upper);

    for (std::size_t comp = 0; comp < upper; ++comp) {
        const double sigma = s_view(static_cast<py::ssize_t>(comp));
        if (!std::isfinite(sigma) || sigma <= 1e-12) {
            continue;
        }
        std::vector<double> u(rows, 0.0);
        std::vector<double> v(k, 0.0);
        for (std::size_t row = 0; row < rows; ++row) {
            u[row] = u_view(static_cast<py::ssize_t>(row), static_cast<py::ssize_t>(comp));
        }
        for (std::size_t col = 0; col < k; ++col) {
            v[col] = vt_view(static_cast<py::ssize_t>(comp), static_cast<py::ssize_t>(col));
        }
        stabilize_component_sign(u, v);

        std::vector<double> mode(length * channels, 0.0);
        for (std::size_t channel = 0; channel < channels; ++channel) {
            const std::size_t offset = channel * window;
            std::vector<double> u_segment(window, 0.0);
            for (std::size_t row = 0; row < window; ++row) {
                u_segment[row] = u[offset + row];
            }
            diagonal_average_rank1_into_mode(u_segment, v, sigma, length, channel, channels, mode);
        }
        modes.insert(modes.end(), mode.begin(), mode.end());
        singular_values.push_back(sigma);
    }

    const std::size_t mode_count = singular_values.size();
    return {std::move(modes), std::move(singular_values), mode_count};
}

ComponentBasis compute_mssa_components_fast(
    const std::vector<double>& X,
    std::size_t rows,
    std::size_t k,
    std::size_t rank,
    std::size_t length,
    std::size_t channels,
    std::size_t window,
    int power_iterations,
    unsigned int seed) {
    std::vector<double> residual = X;
    std::vector<double> modes;
    std::vector<double> singular_values;
    modes.reserve(rank * length * channels);
    singular_values.reserve(rank);

    std::mt19937 rng(seed);
    std::normal_distribution<double> dist(0.0, 1.0);

    for (std::size_t comp = 0; comp < rank; ++comp) {
        std::vector<double> v(k, 0.0);
        for (double& value : v) {
            value = dist(rng);
        }
        normalize_inplace(v);
        std::vector<double> u(rows, 0.0);

        for (int iter = 0; iter < std::max(power_iterations, 2); ++iter) {
            u = trajectory_matvec(residual, rows, k, v);
            normalize_inplace(u);
            v = trajectory_t_matvec(residual, rows, k, u);
            normalize_inplace(v);
        }

        auto xv = trajectory_matvec(residual, rows, k, v);
        const double sigma = dot(u, xv);
        if (!std::isfinite(sigma) || std::abs(sigma) <= 1e-10) {
            break;
        }
        stabilize_component_sign(u, v);

        std::vector<double> mode(length * channels, 0.0);
        for (std::size_t channel = 0; channel < channels; ++channel) {
            const std::size_t offset = channel * window;
            std::vector<double> u_segment(window, 0.0);
            for (std::size_t row = 0; row < window; ++row) {
                u_segment[row] = u[offset + row];
            }
            diagonal_average_rank1_into_mode(u_segment, v, sigma, length, channel, channels, mode);
        }
        modes.insert(modes.end(), mode.begin(), mode.end());
        singular_values.push_back(sigma);

        for (std::size_t i = 0; i < rows; ++i) {
            const std::size_t base = i * k;
            for (std::size_t j = 0; j < k; ++j) {
                residual[base + j] -= sigma * u[i] * v[j];
            }
        }
    }

    const std::size_t mode_count = singular_values.size();
    return {std::move(modes), std::move(singular_values), mode_count};
}

std::vector<double> aggregate_mode_mean(
    const std::vector<double>& modes,
    std::size_t mode,
    std::size_t length,
    std::size_t channels) {
    std::vector<double> out(length, 0.0);
    const std::size_t mode_base = mode * length * channels;
    for (std::size_t t = 0; t < length; ++t) {
        double acc = 0.0;
        for (std::size_t c = 0; c < channels; ++c) {
            acc += modes[mode_base + t * channels + c];
        }
        out[t] = acc / static_cast<double>(channels);
    }
    return out;
}

std::vector<double> sum_modes(
    const std::vector<double>& modes,
    const std::vector<int>& indices,
    std::size_t mode_count,
    std::size_t length,
    std::size_t channels) {
    std::vector<double> out(length * channels, 0.0);
    for (int raw_idx : indices) {
        if (raw_idx < 0 || static_cast<std::size_t>(raw_idx) >= mode_count) {
            continue;
        }
        const std::size_t mode = static_cast<std::size_t>(raw_idx);
        const std::size_t mode_base = mode * length * channels;
        for (std::size_t i = 0; i < length * channels; ++i) {
            out[i] += modes[mode_base + i];
        }
    }
    return out;
}

std::vector<double> subtract_matrix_components(
    const std::vector<double>& y,
    const std::vector<double>& trend,
    const std::vector<double>& season) {
    std::vector<double> out(y.size(), 0.0);
    for (std::size_t i = 0; i < y.size(); ++i) {
        out[i] = y[i] - trend[i] - season[i];
    }
    return out;
}

}  // namespace

py::dict mssa_decompose(
    const py::array_t<double, py::array::c_style | py::array::forcecast>& y_arr,
    int window,
    int rank,
    const std::vector<int>& trend_components,
    const std::vector<int>& season_components,
    double fs,
    const py::object& primary_period_obj,
    double season_freq_tol_ratio,
    const py::object& trend_freq_threshold_obj,
    const std::string& speed_mode,
    int power_iterations,
    unsigned int seed) {
    std::size_t length = 0;
    std::size_t channels = 0;
    auto y = as_matrix_vector(y_arr, length, channels);
    if (length < 4) {
        throw std::invalid_argument("MSSA requires length >= 4.");
    }
    if (channels < 2) {
        throw std::invalid_argument("MSSA requires at least two channels.");
    }

    std::size_t L = static_cast<std::size_t>(window);
    if (L < 2 || L >= length) {
        throw std::invalid_argument("MSSA window must satisfy 2 <= window < len(y).");
    }
    const std::size_t K = length - L + 1;
    const std::size_t rows = L * channels;
    const std::size_t d = std::min<std::size_t>(
        static_cast<std::size_t>(std::max(rank, 1)),
        std::min(rows, K));

    auto X = build_mssa_trajectory_matrix(y, length, channels, L, K);
    ComponentBasis basis;
    if (speed_mode == "fast") {
        basis = compute_mssa_components_fast(
            X,
            rows,
            K,
            d,
            length,
            channels,
            L,
            power_iterations,
            seed);
    } else if (speed_mode == "exact") {
        basis = compute_mssa_components_exact(X, rows, K, d, length, channels, L);
    } else {
        throw std::invalid_argument("MSSA native speed_mode must be 'exact' or 'fast'.");
    }

    std::vector<int> trend_idx = trend_components;
    std::vector<int> season_idx = season_components;
    std::vector<double> dom_freqs;
    dom_freqs.reserve(basis.mode_count);
    for (std::size_t i = 0; i < basis.mode_count; ++i) {
        dom_freqs.push_back(dominant_frequency_grid(aggregate_mode_mean(basis.modes, i, length, channels), fs)[0]);
    }

    if (trend_idx.empty() && season_idx.empty()) {
        if (!primary_period_obj.is_none()) {
            const double primary_period = primary_period_obj.cast<double>();
            const double f0 = primary_period > 0.0 ? (1.0 / primary_period) : 0.0;
            double low_thr = f0 > 0.0 ? f0 / 4.0 : 0.05;
            if (!trend_freq_threshold_obj.is_none()) {
                low_thr = trend_freq_threshold_obj.cast<double>();
            }
            const double tol = season_freq_tol_ratio * f0;
            for (std::size_t i = 0; i < basis.mode_count; ++i) {
                const double freq = dom_freqs[i];
                if (freq <= std::max(low_thr, 1e-8)) {
                    trend_idx.push_back(static_cast<int>(i));
                } else if (f0 > 0.0 && std::abs(freq - f0) <= std::max(tol, 1e-8)) {
                    season_idx.push_back(static_cast<int>(i));
                }
            }
            if (trend_idx.empty() && basis.mode_count >= 1) {
                trend_idx.push_back(0);
            }
            if (season_idx.empty()) {
                for (std::size_t i = 0; i < basis.mode_count; ++i) {
                    if (std::find(trend_idx.begin(), trend_idx.end(), static_cast<int>(i)) == trend_idx.end()) {
                        season_idx.push_back(static_cast<int>(i));
                        break;
                    }
                }
            }
        } else {
            if (basis.mode_count >= 1) trend_idx.push_back(0);
            if (basis.mode_count >= 2) trend_idx.push_back(1);
            if (basis.mode_count >= 4) {
                season_idx.push_back(2);
                season_idx.push_back(3);
            } else if (basis.mode_count >= 3) {
                season_idx.push_back(2);
            }
        }
    }

    auto trend = sum_modes(basis.modes, trend_idx, basis.mode_count, length, channels);
    auto season = sum_modes(basis.modes, season_idx, basis.mode_count, length, channels);
    auto residual = subtract_matrix_components(y, trend, season);

    py::dict components;
    components["modes"] = to_numpy_modes(basis.modes, basis.mode_count, length, channels);

    py::dict meta;
    meta["method"] = "MSSA_NATIVE";
    meta["window"] = static_cast<int>(L);
    meta["rank"] = static_cast<int>(d);
    meta["n_channels"] = static_cast<int>(channels);
    meta["singular_values"] = basis.singular_values;
    meta["trend_components"] = trend_idx;
    meta["season_components"] = season_idx;
    meta["dominant_frequencies"] = dom_freqs;
    meta["native_solver"] = speed_mode == "fast" ? "power-iteration" : "numpy-svd";
    meta["speed_mode"] = speed_mode;

    py::dict out;
    out["trend"] = to_numpy_matrix_2d(trend, length, channels);
    out["season"] = to_numpy_matrix_2d(season, length, channels);
    out["residual"] = to_numpy_matrix_2d(residual, length, channels);
    out["components"] = std::move(components);
    out["meta"] = std::move(meta);
    return out;
}

}  // namespace tsdecomp_native
