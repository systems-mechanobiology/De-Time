cmake_minimum_required(VERSION 3.24)

project(tsdecomp LANGUAGES CXX)

set(PYBIND11_FINDPYTHON ON)
find_package(Python COMPONENTS Interpreter Development REQUIRED)
find_package(pybind11 CONFIG REQUIRED)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(TSDECOMP_NATIVE_SOURCES)
file(GLOB TSDECOMP_NATIVE_GLOB
  "${CMAKE_CURRENT_SOURCE_DIR}/native/*.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/native/*.cc"
  "${CMAKE_CURRENT_SOURCE_DIR}/native/*.cxx"
  "${CMAKE_CURRENT_SOURCE_DIR}/native/src/*.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/native/src/*.cc"
  "${CMAKE_CURRENT_SOURCE_DIR}/native/src/*.cxx"
)
list(SORT TSDECOMP_NATIVE_GLOB)
if(TSDECOMP_NATIVE_GLOB)
  set(TSDECOMP_NATIVE_SOURCES ${TSDECOMP_NATIVE_GLOB})
else()
  set(TSDECOMP_NATIVE_FALLBACK "${CMAKE_CURRENT_BINARY_DIR}/_tsdecomp_native_fallback.cpp")
  file(WRITE "${TSDECOMP_NATIVE_FALLBACK}" [=[
#include <pybind11/pybind11.h>
#include <string>

namespace py = pybind11;

PYBIND11_MODULE(_tsdecomp_native, m) {
  m.doc() = "Fallback tsdecomp native extension.";
  m.def("backend_name", []() { return std::string("fallback"); });
  m.def("has_native_sources", []() { return false; });
}
]=])
  set(TSDECOMP_NATIVE_SOURCES "${TSDECOMP_NATIVE_FALLBACK}")
endif()

pybind11_add_module(_tsdecomp_native MODULE ${TSDECOMP_NATIVE_SOURCES})
target_compile_features(_tsdecomp_native PRIVATE cxx_std_17)
target_include_directories(
  _tsdecomp_native
  PRIVATE
    "${CMAKE_CURRENT_SOURCE_DIR}/native"
    "${CMAKE_CURRENT_SOURCE_DIR}/native/src"
)

install(
  DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/src/detime/"
  DESTINATION "detime"
  FILES_MATCHING
  PATTERN "__pycache__" EXCLUDE
  PATTERN "*.py"
)
install(
  DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/src/tsdecomp/"
  DESTINATION "tsdecomp"
  FILES_MATCHING
  PATTERN "__pycache__" EXCLUDE
  PATTERN "*.py"
)
install(
  DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/src/synthetic_ts_bench/"
  DESTINATION "synthetic_ts_bench"
  FILES_MATCHING
  PATTERN "__pycache__" EXCLUDE
  PATTERN "*.py"
)
install(TARGETS _tsdecomp_native DESTINATION "tsdecomp")
