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

std::vector<double> build_left_gram_matrix(
    const std::vector<double>& X,
    std::size_t rows,
    std::size_t cols) {
    std::vector<double> gram(rows * rows, 0.0);
    for (std::size_t i = 0; i < rows; ++i) {
        const std::size_t base_i = i * cols;
        for (std::size_t j = i; j < rows; ++j) {
            const std::size_t base_j = j * cols;
            double acc = 0.0;
            for (std::size_t k = 0; k < cols; ++k) {
                acc += X[base_i + k] * X[base_j + k];
            }
            gram[i * rows + j] = acc;
            gram[j * rows + i] = acc;
        }
    }
    return gram;
}

struct SymmetricEigenDecomposition {
    std::vector<double> eigenvalues;
    std::vector<double> eigenvectors;
};

SymmetricEigenDecomposition jacobi_eigendecomposition(
    const std::vector<double>& input,
    std::size_t n,
    int max_sweeps = 128,
    double tolerance = 1e-12) {
    std::vector<double> matrix = input;
    std::vector<double> eigenvectors(n * n, 0.0);
    for (std::size_t i = 0; i < n; ++i) {
        eigenvectors[i * n + i] = 1.0;
    }

    for (int sweep = 0; sweep < max_sweeps; ++sweep) {
        std::size_t p = 0;
        std::size_t q = 0;
        double max_off_diag = 0.0;
        for (std::size_t i = 0; i < n; ++i) {
            for (std::size_t j = i + 1; j < n; ++j) {
                const double value = std::abs(matrix[i * n + j]);
                if (value > max_off_diag) {
                    max_off_diag = value;
                    p = i;
                    q = j;
                }
            }
        }

        if (max_off_diag <= tolerance) {
            break;
        }

        const double app = matrix[p * n + p];
        const double aqq = matrix[q * n + q];
        const double apq = matrix[p * n + q];
        if (std::abs(apq) <= tolerance) {
            continue;
        }

        const double tau = (aqq - app) / (2.0 * apq);
        const double t = (tau >= 0.0 ? 1.0 : -1.0) /
            (std::abs(tau) + std::sqrt(1.0 + tau * tau));
        const double c = 1.0 / std::sqrt(1.0 + t * t);
        const double s = t * c;

        for (std::size_t k = 0; k < n; ++k) {
            if (k == p || k == q) {
                continue;
            }
            const double aik = matrix[k * n + p];
            const double akq = matrix[k * n + q];
            const double new_aik = c * aik - s * akq;
            const double new_akq = s * aik + c * akq;
            matrix[k * n + p] = new_aik;
            matrix[p * n + k] = new_aik;
            matrix[k * n + q] = new_akq;
            matrix[q * n + k] = new_akq;
        }

        matrix[p * n + p] = c * c * app - 2.0 * s * c * apq + s * s * aqq;
        matrix[q * n + q] = s * s * app + 2.0 * s * c * apq + c * c * aqq;
        matrix[p * n + q] = 0.0;
        matrix[q * n + p] = 0.0;

        for (std::size_t k = 0; k < n; ++k) {
            const double vip = eigenvectors[k * n + p];
            const double viq = eigenvectors[k * n + q];
            eigenvectors[k * n + p] = c * vip - s * viq;
            eigenvectors[k * n + q] = s * vip + c * viq;
        }
    }

    std::vector<double> eigenvalues(n, 0.0);
    for (std::size_t i = 0; i < n; ++i) {
        eigenvalues[i] = matrix[i * n + i];
    }
    return {std::move(eigenvalues), std::move(eigenvectors)};
}

std::vector<double> matrix_column(
    const std::vector<double>& matrix,
    std::size_t rows,
    std::size_t cols,
    std::size_t column) {
    std::vector<double> out(rows, 0.0);
    if (column >= cols) {
        return out;
    }
    for (std::size_t row = 0; row < rows; ++row) {
        out[row] = matrix[row * cols + column];
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

std::pair<std::vector<std::vector<double>>, std::vector<double>> compute_ssa_components_exact(
    const std::vector<double>& X,
    std::size_t L,
    std::size_t K,
    std::size_t d,
    std::size_t T) {
    py::module_ np_linalg = py::module_::import("numpy.linalg");
    py::tuple svd = np_linalg.attr("svd")(to_numpy_matrix(X, L, K), py::arg("full_matrices") = false);
    auto U = svd[0].cast<py::array_t<double, py::array::c_style | py::array::forcecast>>();
    auto singular = svd[1].cast<py::array_t<double, py::array::c_style | py::array::forcecast>>();
    auto Vt = svd[2].cast<py::array_t<double, py::array::c_style | py::array::forcecast>>();

    auto u_view = U.unchecked<2>();
    auto s_view = singular.unchecked<1>();
    auto vt_view = Vt.unchecked<2>();
    std::vector<std::vector<double>> rc_list;
    std::vector<double> singular_values;
    rc_list.reserve(d);
    singular_values.reserve(d);

    const std::size_t upper = std::min<std::size_t>(d, static_cast<std::size_t>(s_view.shape(0)));
    for (std::size_t comp = 0; comp < upper; ++comp) {
        const double sigma = s_view(static_cast<py::ssize_t>(comp));
        if (!std::isfinite(sigma) || sigma <= 1e-12) {
            continue;
        }
        std::vector<double> u(L, 0.0);
        std::vector<double> v(K, 0.0);
        for (std::size_t row = 0; row < L; ++row) {
            u[row] = u_view(static_cast<py::ssize_t>(row), static_cast<py::ssize_t>(comp));
        }
        for (std::size_t col = 0; col < K; ++col) {
            v[col] = vt_view(static_cast<py::ssize_t>(comp), static_cast<py::ssize_t>(col));
        }
        stabilize_component_sign(u, v);

        rc_list.push_back(diagonal_average_rank1(u, v, sigma, T));
        singular_values.push_back(sigma);
    }

    return {std::move(rc_list), std::move(singular_values)};
}

std::pair<std::vector<std::vector<double>>, std::vector<double>> compute_ssa_components_fast(
    const std::vector<double>& X,
    std::size_t L,
    std::size_t K,
    std::size_t d,
    std::size_t T,
    int power_iterations,
    unsigned int seed) {
    std::vector<double> residual = X;
    std::vector<std::vector<double>> rc_list;
    std::vector<double> singular_values;
    rc_list.reserve(d);
    singular_values.reserve(d);

    std::mt19937 rng(seed);
    std::normal_distribution<double> dist(0.0, 1.0);

    for (std::size_t comp = 0; comp < d; ++comp) {
        std::vector<double> v(K, 0.0);
        for (double& value : v) {
            value = dist(rng);
        }
        normalize_inplace(v);
        std::vector<double> u(L, 0.0);

        for (int iter = 0; iter < std::max(power_iterations, 2); ++iter) {
            u = trajectory_matvec(residual, L, K, v);
            normalize_inplace(u);
            v = trajectory_t_matvec(residual, L, K, u);
            normalize_inplace(v);
        }

        auto xv = trajectory_matvec(residual, L, K, v);
        const double sigma = dot(u, xv);
        if (!std::isfinite(sigma) || std::abs(sigma) <= 1e-10) {
            break;
        }

        stabilize_component_sign(u, v);
        rc_list.push_back(diagonal_average_rank1(u, v, sigma, T));
        singular_values.push_back(sigma);

        for (std::size_t i = 0; i < L; ++i) {
            const std::size_t base = i * K;
            for (std::size_t j = 0; j < K; ++j) {
                residual[base + j] -= sigma * u[i] * v[j];
            }
        }
    }

    return {std::move(rc_list), std::move(singular_values)};
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
    const std::string& speed_mode,
    int power_iterations,
    unsigned int seed) {
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

    auto X = build_trajectory_matrix(y, L, K);
    std::vector<std::vector<double>> rc_list;
    std::vector<double> singular_values;
    if (speed_mode == "fast") {
        auto components = compute_ssa_components_fast(X, L, K, d, T, power_iterations, seed);
        rc_list = std::move(components.first);
        singular_values = std::move(components.second);
    } else if (speed_mode == "exact") {
        auto components = compute_ssa_components_exact(X, L, K, d, T);
        rc_list = std::move(components.first);
        singular_values = std::move(components.second);
    } else {
        throw std::invalid_argument("SSA native speed_mode must be 'exact' or 'fast'.");
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
    meta["native_solver"] = speed_mode == "fast" ? "power-iteration" : "jacobi-eigen";
    meta["speed_mode"] = speed_mode;
    return to_python_result({trend, season, residual}, std::move(meta));
}

}  // namespace tsdecomp_native
