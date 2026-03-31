#pragma once

#include <algorithm>
#include <cmath>
#include <cstddef>
#include <limits>
#include <numeric>
#include <random>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

namespace tsdecomp_native {

constexpr double kPi = 3.141592653589793238462643383279502884;

struct DecompositionResult {
    std::vector<double> trend;
    std::vector<double> season;
    std::vector<double> residual;
};

inline py::array_t<double> to_numpy(const std::vector<double>& values) {
    auto out = py::array_t<double>(values.size());
    auto buf = out.mutable_unchecked<1>();
    for (py::ssize_t i = 0; i < buf.shape(0); ++i) {
        buf(i) = values[static_cast<std::size_t>(i)];
    }
    return out;
}

inline py::dict to_python_result(
    const DecompositionResult& result,
    py::dict meta = py::dict()) {
    py::dict out;
    out["trend"] = to_numpy(result.trend);
    out["season"] = to_numpy(result.season);
    out["residual"] = to_numpy(result.residual);
    out["meta"] = std::move(meta);
    return out;
}

inline std::vector<double> as_vector(const py::array_t<double, py::array::c_style | py::array::forcecast>& arr) {
    if (arr.ndim() != 1) {
        throw std::invalid_argument("Input series must be a 1D float64 array.");
    }
    const auto n = static_cast<std::size_t>(arr.shape(0));
    std::vector<double> out(n);
    auto view = arr.unchecked<1>();
    for (std::size_t i = 0; i < n; ++i) {
        out[i] = view(static_cast<py::ssize_t>(i));
    }
    return out;
}

inline double l2_norm(const std::vector<double>& x) {
    double acc = 0.0;
    for (double v : x) {
        acc += v * v;
    }
    return std::sqrt(acc);
}

inline double dot(const std::vector<double>& a, const std::vector<double>& b) {
    if (a.size() != b.size()) {
        throw std::invalid_argument("dot: vector size mismatch.");
    }
    double acc = 0.0;
    for (std::size_t i = 0; i < a.size(); ++i) {
        acc += a[i] * b[i];
    }
    return acc;
}

inline void normalize_inplace(std::vector<double>& x) {
    const double nrm = l2_norm(x);
    if (nrm <= std::numeric_limits<double>::epsilon()) {
        return;
    }
    for (double& v : x) {
        v /= nrm;
    }
}

inline std::vector<double> dominant_frequency_grid(
    const std::vector<double>& x,
    double fs) {
    const std::size_t n = x.size();
    if (n < 4 || fs <= 0.0) {
        return {0.0, 0.0};
    }
    double best_power = -1.0;
    double best_freq = 0.0;
    const std::size_t k_max = n / 2;
    for (std::size_t k = 1; k <= k_max; ++k) {
        const double omega = 2.0 * kPi * static_cast<double>(k) / static_cast<double>(n);
        double re = 0.0;
        double im = 0.0;
        for (std::size_t t = 0; t < n; ++t) {
            const double angle = omega * static_cast<double>(t);
            re += x[t] * std::cos(angle);
            im -= x[t] * std::sin(angle);
        }
        const double power = re * re + im * im;
        if (power > best_power) {
            best_power = power;
            best_freq = static_cast<double>(k) * fs / static_cast<double>(n);
        }
    }
    return {best_freq, best_power};
}

inline std::vector<double> sum_components(
    const std::vector<std::vector<double>>& components,
    const std::vector<int>& indices,
    std::size_t length) {
    std::vector<double> out(length, 0.0);
    for (int idx : indices) {
        if (idx < 0 || static_cast<std::size_t>(idx) >= components.size()) {
            continue;
        }
        const auto& comp = components[static_cast<std::size_t>(idx)];
        for (std::size_t i = 0; i < length; ++i) {
            out[i] += comp[i];
        }
    }
    return out;
}

inline std::vector<double> subtract_vectors(
    const std::vector<double>& a,
    const std::vector<double>& b,
    const std::vector<double>& c) {
    if (a.size() != b.size() || a.size() != c.size()) {
        throw std::invalid_argument("subtract_vectors: size mismatch.");
    }
    std::vector<double> out(a.size());
    for (std::size_t i = 0; i < a.size(); ++i) {
        out[i] = a[i] - b[i] - c[i];
    }
    return out;
}

}  // namespace tsdecomp_native
