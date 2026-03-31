#include <cctype>

#include "common.hpp"

namespace tsdecomp_native {

namespace {

int infer_period(const std::vector<double>& y, int max_period_search) {
    const std::size_t n = y.size();
    if (n < 4) {
        return static_cast<int>(std::max<std::size_t>(1, n));
    }

    auto freq_info = dominant_frequency_grid(y, 1.0);
    const double freq = freq_info[0];
    if (freq <= 1e-12) {
        return std::max(2, std::min(max_period_search, std::max(2, static_cast<int>(n / 4))));
    }

    const int period = static_cast<int>(std::llround(1.0 / freq));
    return std::max(2, std::min({period, max_period_search, static_cast<int>(n)}));
}

}  // namespace

py::dict std_decompose(
    const py::array_t<double, py::array::c_style | py::array::forcecast>& y_arr,
    py::object period_obj,
    const std::string& variant,
    int max_period_search,
    double eps) {
    auto y = as_vector(y_arr);
    const std::size_t n = y.size();
    const std::string variant_upper = [&variant]() {
        std::string out = variant;
        std::transform(out.begin(), out.end(), out.begin(), [](unsigned char c) {
            return static_cast<char>(std::toupper(c));
        });
        return out;
    }();
    if (variant_upper != "STD" && variant_upper != "STDR") {
        throw std::invalid_argument("STD native kernel variant must be 'STD' or 'STDR'.");
    }

    int period = period_obj.is_none() ? infer_period(y, max_period_search) : period_obj.cast<int>();
    if (n == 0) {
        py::dict meta;
        meta["method"] = variant_upper + "_NATIVE";
        meta["period"] = 0;
        meta["n_cycles"] = 0;
        meta["incomplete_cycle"] = false;
        py::dict components;
        components["dispersion"] = py::array_t<double>(0);
        components["seasonal_shape"] = py::array_t<double>(0);
        py::dict out;
        out["trend"] = py::array_t<double>(0);
        out["season"] = py::array_t<double>(0);
        out["residual"] = py::array_t<double>(0);
        out["components"] = std::move(components);
        out["meta"] = std::move(meta);
        return out;
    }

    period = std::max(1, std::min(period, static_cast<int>(n)));

    std::vector<double> trend(n, 0.0);
    std::vector<double> season(n, 0.0);
    std::vector<double> residual(n, 0.0);
    std::vector<double> dispersion(n, 0.0);
    std::vector<double> seasonal_shape(n, 0.0);
    std::vector<std::vector<double>> block_shapes;
    std::vector<std::pair<std::size_t, std::size_t>> block_ranges;

    for (std::size_t start = 0; start < n; start += static_cast<std::size_t>(period)) {
        const std::size_t stop = std::min(n, start + static_cast<std::size_t>(period));
        const std::size_t block_size = stop - start;
        double mean = 0.0;
        for (std::size_t i = start; i < stop; ++i) {
            mean += y[i];
        }
        mean /= static_cast<double>(block_size);

        std::vector<double> centered(block_size, 0.0);
        double div = 0.0;
        for (std::size_t i = 0; i < block_size; ++i) {
            centered[i] = y[start + i] - mean;
            div += centered[i] * centered[i];
        }
        div = std::sqrt(div);

        std::vector<double> shape(block_size, 0.0);
        if (div > eps) {
            for (std::size_t i = 0; i < block_size; ++i) {
                shape[i] = centered[i] / div;
            }
        } else {
            div = 0.0;
        }

        for (std::size_t i = start; i < stop; ++i) {
            trend[i] = mean;
            dispersion[i] = div;
        }
        for (std::size_t i = 0; i < block_size; ++i) {
            seasonal_shape[start + i] = shape[i];
            season[start + i] = div * shape[i];
        }

        block_shapes.push_back(shape);
        block_ranges.emplace_back(start, stop);
    }

    py::dict components;
    if (variant_upper == "STDR") {
        std::vector<double> avg_shape(static_cast<std::size_t>(period), 0.0);
        std::vector<double> counts(static_cast<std::size_t>(period), 0.0);
        for (const auto& shape : block_shapes) {
            for (std::size_t i = 0; i < shape.size(); ++i) {
                avg_shape[i] += shape[i];
                counts[i] += 1.0;
            }
        }
        for (std::size_t i = 0; i < avg_shape.size(); ++i) {
            if (counts[i] > 0.0) {
                avg_shape[i] /= counts[i];
            }
        }

        std::fill(season.begin(), season.end(), 0.0);
        std::fill(seasonal_shape.begin(), seasonal_shape.end(), 0.0);
        for (const auto& range : block_ranges) {
            const std::size_t start = range.first;
            const std::size_t stop = range.second;
            for (std::size_t i = 0; start + i < stop; ++i) {
                seasonal_shape[start + i] = avg_shape[i];
                season[start + i] = dispersion[start + i] * avg_shape[i];
            }
        }
        components["average_seasonal_shape"] = to_numpy(avg_shape);
    }

    for (std::size_t i = 0; i < n; ++i) {
        residual[i] = y[i] - trend[i] - season[i];
    }

    components["dispersion"] = to_numpy(dispersion);
    components["seasonal_shape"] = to_numpy(seasonal_shape);

    py::dict meta;
    meta["method"] = variant_upper + "_NATIVE";
    meta["period"] = period;
    meta["n_cycles"] = static_cast<int>(block_ranges.size());
    meta["incomplete_cycle"] = static_cast<bool>(n % static_cast<std::size_t>(period));

    py::dict out;
    out["trend"] = to_numpy(trend);
    out["season"] = to_numpy(season);
    out["residual"] = to_numpy(residual);
    out["components"] = std::move(components);
    out["meta"] = std::move(meta);
    return out;
}

}  // namespace tsdecomp_native
