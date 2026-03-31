#include "common.hpp"

namespace tsdecomp_native {

namespace {

std::vector<double> trajectory_matvec(
    const std::vector<double>& X,
    std::size_t rows,
    std::size_t cols,
    const std::vector<double>& v) {
    std::vector<double> out(rows, 0.0);
    for (std::size_t i = 0; i < rows; ++i) {
        double acc = 0.0;
        const std::size_t base = i * cols;
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

std::vector<double> diagonal_average_rank1(
    const std::vector<double>& u,
    const std::vector<double>& v,
    double sigma,
    std::size_t length) {
    const std::size_t rows = u.size();
    const std::size_t cols = v.size();
    std::vector<double> recon(length, 0.0);
    std::vector<double> counts(length, 0.0);
    for (std::size_t i = 0; i < rows; ++i) {
        for (std::size_t j = 0; j < cols; ++j) {
            const std::size_t idx = i + j;
            recon[idx] += sigma * u[i] * v[j];
            counts[idx] += 1.0;
        }
    }
    for (std::size_t i = 0; i < length; ++i) {
        if (counts[i] > 0.0) {
            recon[i] /= counts[i];
        }
    }
    return recon;
}

std::vector<double> build_trajectory_matrix(
    const std::vector<double>& y,
    std::size_t window,
    std::size_t k) {
    std::vector<double> X(window * k, 0.0);
    for (std::size_t col = 0; col < k; ++col) {
        for (std::size_t row = 0; row < window; ++row) {
            X[row * k + col] = y[col + row];
        }
    }
    return X;
}

}  // namespace

py::dict ssa_decompose(
    const py::array_t<double, py::array::c_style | py::array::forcecast>& y_arr,
    int window,
    int rank,
    const std::vector<int>& trend_components,
    const std::vector<int>& season_components,
    double fs,
    const py::object& primary_period_obj,
    double season_freq_tol_ratio,
    const py::object& trend_freq_threshold_obj,
    int power_iterations,
    unsigned int seed) {
    (void) season_freq_tol_ratio;

    auto y = as_vector(y_arr);
    const std::size_t T = y.size();
    if (T < 4) {
        throw std::invalid_argument("SSA requires series length >= 4.");
    }
    std::size_t L = static_cast<std::size_t>(window);
    if (L < 2 || L >= T) {
        throw std::invalid_argument("SSA window must satisfy 2 <= window < len(y).");
    }
    const std::size_t K = T - L + 1;
    const std::size_t d = std::min<std::size_t>(
        static_cast<std::size_t>(std::max(rank, 1)),
        std::min(L, K));

    auto X_res = build_trajectory_matrix(y, L, K);
    std::vector<std::vector<double>> rc_list;
    rc_list.reserve(d);
    std::vector<double> singular_values;
    singular_values.reserve(d);

    std::mt19937 rng(seed);
    std::normal_distribution<double> dist(0.0, 1.0);

    for (std::size_t comp = 0; comp < d; ++comp) {
        std::vector<double> v(K);
        for (double& val : v) {
            val = dist(rng);
        }
        normalize_inplace(v);
        std::vector<double> u(L, 0.0);

        for (int iter = 0; iter < std::max(power_iterations, 2); ++iter) {
            u = trajectory_matvec(X_res, L, K, v);
            normalize_inplace(u);
            v = trajectory_t_matvec(X_res, L, K, u);
            normalize_inplace(v);
        }

        auto xv = trajectory_matvec(X_res, L, K, v);
        const double sigma = dot(u, xv);
        if (!std::isfinite(sigma) || std::abs(sigma) <= 1e-10) {
            break;
        }

        rc_list.push_back(diagonal_average_rank1(u, v, sigma, T));
        singular_values.push_back(sigma);

        for (std::size_t i = 0; i < L; ++i) {
            const std::size_t base = i * K;
            for (std::size_t j = 0; j < K; ++j) {
                X_res[base + j] -= sigma * u[i] * v[j];
            }
        }
    }

    std::vector<int> trend_idx = trend_components;
    std::vector<int> season_idx = season_components;
    const std::size_t num_rc = rc_list.size();

    if (trend_idx.empty() && season_idx.empty()) {
        if (!primary_period_obj.is_none()) {
            const double primary_period = primary_period_obj.cast<double>();
            const double f0 = primary_period > 0.0 ? (1.0 / primary_period) : 0.0;
            double low_thr = f0 > 0.0 ? f0 / 4.0 : 0.05;
            if (!trend_freq_threshold_obj.is_none()) {
                low_thr = trend_freq_threshold_obj.cast<double>();
            }
            const double tol = season_freq_tol_ratio * f0;
            for (std::size_t i = 0; i < num_rc; ++i) {
                const auto freq = dominant_frequency_grid(rc_list[i], fs)[0];
                if (freq <= std::max(low_thr, 1e-8)) {
                    trend_idx.push_back(static_cast<int>(i));
                } else if (f0 > 0.0 && std::abs(freq - f0) <= std::max(tol, 1e-8)) {
                    season_idx.push_back(static_cast<int>(i));
                }
            }
            if (trend_idx.empty() && num_rc >= 1) {
                trend_idx.push_back(0);
            }
            if (season_idx.empty()) {
                for (std::size_t i = 0; i < num_rc; ++i) {
                    if (std::find(trend_idx.begin(), trend_idx.end(), static_cast<int>(i)) == trend_idx.end()) {
                        season_idx.push_back(static_cast<int>(i));
                        break;
                    }
                }
            }
        } else {
            if (num_rc >= 1) trend_idx.push_back(0);
            if (num_rc >= 2) trend_idx.push_back(1);
            if (num_rc >= 4) {
                season_idx.push_back(2);
                season_idx.push_back(3);
            } else if (num_rc >= 3) {
                season_idx.push_back(2);
            }
        }
    }

    auto trend = sum_components(rc_list, trend_idx, T);
    auto season = sum_components(rc_list, season_idx, T);
    auto residual = subtract_vectors(y, trend, season);

    py::dict meta;
    meta["method"] = "SSA_NATIVE";
    meta["window"] = window;
    meta["rank"] = rank;
    meta["components"] = static_cast<int>(num_rc);
    meta["singular_values"] = singular_values;
    meta["trend_components"] = trend_idx;
    meta["season_components"] = season_idx;
    return to_python_result({trend, season, residual}, std::move(meta));
}

}  // namespace tsdecomp_native
