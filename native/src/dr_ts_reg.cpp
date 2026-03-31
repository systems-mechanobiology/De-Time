#include "common.hpp"

namespace tsdecomp_native {

namespace {

void apply_d2t_d2(const std::vector<double>& x, std::vector<double>& out) {
    const std::size_t n = x.size();
    out.assign(n, 0.0);
    if (n < 3) {
        return;
    }
    for (std::size_t i = 0; i + 2 < n; ++i) {
        const double diff = x[i] - 2.0 * x[i + 1] + x[i + 2];
        out[i] += diff;
        out[i + 1] += -2.0 * diff;
        out[i + 2] += diff;
    }
}

void apply_spt_sp(const std::vector<double>& x, int period, std::vector<double>& out) {
    const std::size_t n = x.size();
    out.assign(n, 0.0);
    const std::size_t p = static_cast<std::size_t>(std::max(period, 1));
    if (p >= n) {
        return;
    }
    for (std::size_t i = 0; i + p < n; ++i) {
        const double diff = x[i] - x[i + p];
        out[i] += diff;
        out[i + p] -= diff;
    }
}

void apply_system(
    const std::vector<double>& z,
    double alpha,
    double lambda_t,
    double lambda_s,
    int period,
    std::vector<double>& out) {
    const std::size_t total = z.size();
    const std::size_t n = total / 2;
    std::vector<double> trend(z.begin(), z.begin() + static_cast<std::ptrdiff_t>(n));
    std::vector<double> season(z.begin() + static_cast<std::ptrdiff_t>(n), z.end());

    std::vector<double> d2_term;
    std::vector<double> sp_term;
    apply_d2t_d2(trend, d2_term);
    apply_spt_sp(season, period, sp_term);

    out.assign(total, 0.0);
    for (std::size_t i = 0; i < n; ++i) {
        out[i] = alpha * trend[i] + lambda_t * d2_term[i] + alpha * season[i];
        out[n + i] = alpha * trend[i] + alpha * season[i] + lambda_s * sp_term[i];
    }
}

std::vector<double> conjugate_gradient(
    const std::vector<double>& b,
    double alpha,
    double lambda_t,
    double lambda_s,
    int period,
    int max_iter,
    double tol) {
    std::vector<double> x(b.size(), 0.0);
    std::vector<double> r = b;
    std::vector<double> p = r;
    double rs_old = dot(r, r);
    if (std::sqrt(rs_old) <= tol) {
        return x;
    }

    std::vector<double> Ap;
    for (int iter = 0; iter < max_iter; ++iter) {
        apply_system(p, alpha, lambda_t, lambda_s, period, Ap);
        const double denom = dot(p, Ap);
        if (std::abs(denom) <= 1e-14) {
            break;
        }
        const double step = rs_old / denom;
        for (std::size_t i = 0; i < x.size(); ++i) {
            x[i] += step * p[i];
            r[i] -= step * Ap[i];
        }
        const double rs_new = dot(r, r);
        if (std::sqrt(rs_new) <= tol) {
            break;
        }
        const double beta = rs_new / rs_old;
        for (std::size_t i = 0; i < p.size(); ++i) {
            p[i] = r[i] + beta * p[i];
        }
        rs_old = rs_new;
    }
    return x;
}

}  // namespace

py::dict dr_ts_reg_decompose(
    const py::array_t<double, py::array::c_style | py::array::forcecast>& y_arr,
    int period,
    double lambda_t,
    double lambda_s,
    double lambda_r,
    int max_iter,
    double tol) {
    auto y = as_vector(y_arr);
    const std::size_t n = y.size();
    if (n < 3) {
        throw std::invalid_argument("DR_TS_REG requires series length >= 3.");
    }
    period = std::max(1, std::min(period, static_cast<int>(n - 1)));

    const double alpha = 1.0 + lambda_r;
    std::vector<double> b(2 * n, 0.0);
    for (std::size_t i = 0; i < n; ++i) {
        b[i] = alpha * y[i];
        b[n + i] = alpha * y[i];
    }

    auto z = conjugate_gradient(b, alpha, lambda_t, lambda_s, period, max_iter, tol);
    std::vector<double> trend(z.begin(), z.begin() + static_cast<std::ptrdiff_t>(n));
    std::vector<double> season(z.begin() + static_cast<std::ptrdiff_t>(n), z.end());
    auto residual = subtract_vectors(y, trend, season);

    py::dict meta;
    meta["method"] = "DR_TS_REG_NATIVE";
    meta["period"] = period;
    meta["lambda_T"] = lambda_t;
    meta["lambda_S"] = lambda_s;
    meta["lambda_R"] = lambda_r;
    meta["max_iter"] = max_iter;
    meta["tol"] = tol;
    return to_python_result({trend, season, residual}, std::move(meta));
}

}  // namespace tsdecomp_native
