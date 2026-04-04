#include "common.hpp"

namespace tsdecomp_native {

py::dict ssa_decompose(
    const py::array_t<double, py::array::c_style | py::array::forcecast>& y_arr,
    int window,
    int rank,
    const std::vector<int>& trend_components = {},
    const std::vector<int>& season_components = {},
    double fs = 1.0,
    const py::object& primary_period_obj = py::none(),
    double season_freq_tol_ratio = 0.25,
    const py::object& trend_freq_threshold_obj = py::none(),
    int power_iterations = 12,
    unsigned int seed = 42);

py::dict std_decompose(
    const py::array_t<double, py::array::c_style | py::array::forcecast>& y_arr,
    py::object period = py::none(),
    const std::string& variant = "STD",
    int max_period_search = 128,
    double eps = 1e-12);

}  // namespace tsdecomp_native

PYBIND11_MODULE(_detime_native, m) {
    m.doc() = "Native C++ kernels for De-Time.";

    m.def(
        "ssa_decompose",
        &tsdecomp_native::ssa_decompose,
        py::arg("y"),
        py::arg("window"),
        py::arg("rank"),
        py::arg("trend_components") = std::vector<int>{},
        py::arg("season_components") = std::vector<int>{},
        py::arg("fs") = 1.0,
        py::arg("primary_period") = py::none(),
        py::arg("season_freq_tol_ratio") = 0.25,
        py::arg("trend_freq_threshold") = py::none(),
        py::arg("power_iterations") = 12,
        py::arg("seed") = 42);

    m.def(
        "std_decompose",
        &tsdecomp_native::std_decompose,
        py::arg("y"),
        py::arg("period") = py::none(),
        py::arg("variant") = "STD",
        py::arg("max_period_search") = 128,
        py::arg("eps") = 1e-12);
}
