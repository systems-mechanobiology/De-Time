cmake_minimum_required(VERSION 3.24)

project(detime LANGUAGES CXX)

set(PYBIND11_FINDPYTHON ON)
find_package(Python COMPONENTS Interpreter Development REQUIRED)
find_package(pybind11 CONFIG REQUIRED)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(DETIME_NATIVE_SOURCES)
file(GLOB DETIME_NATIVE_GLOB
  "${CMAKE_CURRENT_SOURCE_DIR}/native/*.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/native/*.cc"
  "${CMAKE_CURRENT_SOURCE_DIR}/native/*.cxx"
  "${CMAKE_CURRENT_SOURCE_DIR}/native/src/*.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/native/src/*.cc"
  "${CMAKE_CURRENT_SOURCE_DIR}/native/src/*.cxx"
)
list(FILTER DETIME_NATIVE_GLOB EXCLUDE REGEX ".*/dr_ts_reg\\.cpp$")
list(SORT DETIME_NATIVE_GLOB)
if(DETIME_NATIVE_GLOB)
  set(DETIME_NATIVE_SOURCES ${DETIME_NATIVE_GLOB})
else()
  set(DETIME_NATIVE_FALLBACK "${CMAKE_CURRENT_BINARY_DIR}/_detime_native_fallback.cpp")
  file(WRITE "${DETIME_NATIVE_FALLBACK}" [=[
#include <pybind11/pybind11.h>
#include <string>

namespace py = pybind11;

PYBIND11_MODULE(_detime_native, m) {
  m.doc() = "Fallback detime native extension.";
  m.def("backend_name", []() { return std::string("fallback"); });
  m.def("has_native_sources", []() { return false; });
}
]=])
  set(DETIME_NATIVE_SOURCES "${DETIME_NATIVE_FALLBACK}")
endif()

pybind11_add_module(_detime_native MODULE ${DETIME_NATIVE_SOURCES})
target_compile_features(_detime_native PRIVATE cxx_std_17)
target_include_directories(
  _detime_native
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
  DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/src/detime/schema_assets/"
  DESTINATION "detime/schema_assets"
  FILES_MATCHING
  PATTERN "*.json"
)
install(
  FILES
    "${CMAKE_CURRENT_SOURCE_DIR}/src/tsdecomp/__init__.py"
    "${CMAKE_CURRENT_SOURCE_DIR}/src/tsdecomp/__main__.py"
    "${CMAKE_CURRENT_SOURCE_DIR}/src/tsdecomp/_compat.py"
    "${CMAKE_CURRENT_SOURCE_DIR}/src/tsdecomp/cli.py"
  DESTINATION "tsdecomp"
)
install(TARGETS _detime_native DESTINATION "detime")
