#include "common.hpp"

#include <complex>

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
    const std::string& speed_mode = "exact",
    int power_iterations = 12,
    unsigned int seed = 42);

py::dict std_decompose(
    const py::array_t<double, py::array::c_style | py::array::forcecast>& y_arr,
    py::object period = py::none(),
    const std::string& variant = "STD",
    int max_period_search = 128,
    double eps = 1e-12);

py::dict ma_baseline_decompose(
    const py::array_t<double, py::array::c_style | py::array::forcecast>& y_arr,
    int trend_window,
    const py::object& season_period_obj = py::none());

py::dict mssa_decompose(
    const py::array_t<double, py::array::c_style | py::array::forcecast>& y_arr,
    int window,
    int rank,
    const std::vector<int>& trend_components = {},
    const std::vector<int>& season_components = {},
    double fs = 1.0,
    const py::object& primary_period_obj = py::none(),
    double season_freq_tol_ratio = 0.25,
    const py::object& trend_freq_threshold_obj = py::none(),
    const std::string& speed_mode = "exact",
    int power_iterations = 12,
    unsigned int seed = 42);

py::dict vmd_decompose(
    const py::array_t<double, py::array::c_style | py::array::forcecast>& y_arr,
    double alpha,
    double tau,
    int K,
    int DC,
    int init,
    double tol,
    int max_iter = 500,
    unsigned int seed = 42);

py::array_t<std::complex<float>> gabor_stft_rfft(
    const py::array_t<double, py::array::c_style | py::array::forcecast>& x_arr,
    int win_len,
    int hop,
    int n_fft,
    const py::array_t<double, py::array::c_style | py::array::forcecast>& window_arr);

py::array_t<double> gabor_istft_rfft(
    const py::array_t<std::complex<float>, py::array::c_style | py::array::forcecast>& Z_arr,
    int win_len,
    int hop,
    int n_fft,
    const py::array_t<double, py::array::c_style | py::array::forcecast>& window_arr,
    int length);

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
    int max_clusters = -1,
    double trend_freq_thr = 0.08);

}  // namespace tsdecomp_native

PYBIND11_MODULE(_detime_native, m) {
    m.doc() = "Native C++ kernels for DeTime.";

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
        py::arg("speed_mode") = "exact",
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

    m.def(
        "ma_baseline_decompose",
        &tsdecomp_native::ma_baseline_decompose,
        py::arg("y"),
        py::arg("trend_window"),
        py::arg("season_period") = py::none());

    m.def(
        "mssa_decompose",
        &tsdecomp_native::mssa_decompose,
        py::arg("y"),
        py::arg("window"),
        py::arg("rank"),
        py::arg("trend_components") = std::vector<int>{},
        py::arg("season_components") = std::vector<int>{},
        py::arg("fs") = 1.0,
        py::arg("primary_period") = py::none(),
        py::arg("season_freq_tol_ratio") = 0.25,
        py::arg("trend_freq_threshold") = py::none(),
        py::arg("speed_mode") = "exact",
        py::arg("power_iterations") = 12,
        py::arg("seed") = 42);

    m.def(
        "vmd_decompose",
        &tsdecomp_native::vmd_decompose,
        py::arg("y"),
        py::arg("alpha"),
        py::arg("tau"),
        py::arg("K"),
        py::arg("DC"),
        py::arg("init"),
        py::arg("tol"),
        py::arg("max_iter") = 500,
        py::arg("seed") = 42);

    m.def(
        "gabor_stft_rfft",
        &tsdecomp_native::gabor_stft_rfft,
        py::arg("x"),
        py::arg("win_len"),
        py::arg("hop"),
        py::arg("n_fft"),
        py::arg("window"));

    m.def(
        "gabor_istft_rfft",
        &tsdecomp_native::gabor_istft_rfft,
        py::arg("Z"),
        py::arg("win_len"),
        py::arg("hop"),
        py::arg("n_fft"),
        py::arg("window"),
        py::arg("length"));

    m.def(
        "gabor_cluster_decompose",
        &tsdecomp_native::gabor_cluster_decompose,
        py::arg("x"),
        py::arg("centroids"),
        py::arg("mu"),
        py::arg("sigma"),
        py::arg("win_len"),
        py::arg("hop"),
        py::arg("n_fft"),
        py::arg("window"),
        py::arg("use_log_amp"),
        py::arg("max_clusters") = -1,
        py::arg("trend_freq_thr") = 0.08);
}
