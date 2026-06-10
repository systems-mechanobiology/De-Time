#include "common.hpp"

namespace tsdecomp_native {

namespace {

std::vector<double> centered_moving_average(const std::vector<double>& y, int window) {
    const std::size_t n = y.size();
    window = std::max(1, window);
    std::vector<double> trend(n, 0.0);
    if (n == 0) {
        return trend;
    }
    if (window == 1) {
        return y;
    }

    const int left = window / 2;
    const int right = window - left - 1;
    std::vector<double> prefix(n + 1, 0.0);
    for (std::size_t i = 0; i < n; ++i) {
        prefix[i + 1] = prefix[i] + y[i];
    }

    for (std::size_t i = 0; i < n; ++i) {
        const int raw_start = static_cast<int>(i) - left;
        const int raw_stop = static_cast<int>(i) + right + 1;
        const std::size_t start = static_cast<std::size_t>(std::max(0, raw_start));
        const std::size_t stop = static_cast<std::size_t>(std::min(static_cast<int>(n), raw_stop));
        trend[i] = (prefix[stop] - prefix[start]) / static_cast<double>(window);
    }
    return trend;
}

std::vector<double> seasonal_means(const std::vector<double>& detrended, int period) {
    const std::size_t n = detrended.size();
    period = std::max(1, period);
    std::vector<double> season(n, 0.0);
    std::vector<double> sums(static_cast<std::size_t>(period), 0.0);
    std::vector<int> counts(static_cast<std::size_t>(period), 0);

    for (std::size_t i = 0; i < n; ++i) {
        const std::size_t offset = i % static_cast<std::size_t>(period);
        sums[offset] += detrended[i];
        counts[offset] += 1;
    }
    for (std::size_t i = 0; i < n; ++i) {
        const std::size_t offset = i % static_cast<std::size_t>(period);
        if (counts[offset] > 0) {
            season[i] = sums[offset] / static_cast<double>(counts[offset]);
        }
    }

    double mean = 0.0;
    for (double value : season) {
        mean += value;
    }
    mean = n > 0 ? mean / static_cast<double>(n) : 0.0;
    for (double& value : season) {
        value -= mean;
    }
    return season;
}

}  // namespace

py::dict ma_baseline_decompose(
    const py::array_t<double, py::array::c_style | py::array::forcecast>& y_arr,
    int trend_window,
    const py::object& season_period_obj = py::none()) {
    auto y = as_vector(y_arr);
    const std::size_t n = y.size();
    int window = std::max(1, trend_window);
    if (window % 2 == 0) {
        ++window;
    }

    std::vector<double> trend = centered_moving_average(y, window);
    std::vector<double> detrended(n, 0.0);
    for (std::size_t i = 0; i < n; ++i) {
        detrended[i] = y[i] - trend[i];
    }

    std::vector<double> season(n, 0.0);
    py::object season_meta = py::none();
    if (!season_period_obj.is_none()) {
        const int period = py::cast<int>(season_period_obj);
        if (period > 0) {
            season = seasonal_means(detrended, period);
            season_meta = py::cast(period);
        }
    }

    std::vector<double> residual(n, 0.0);
    for (std::size_t i = 0; i < n; ++i) {
        residual[i] = y[i] - trend[i] - season[i];
    }

    py::dict params;
    params["trend_window"] = window;
    params["season_period"] = season_meta;

    py::dict meta;
    meta["method"] = "MA_BASELINE_NATIVE";
    meta["params"] = params;

    py::dict out;
    out["trend"] = to_numpy(trend);
    out["season"] = to_numpy(season);
    out["residual"] = to_numpy(residual);
    out["meta"] = meta;
    return out;
}

}  // namespace tsdecomp_native
