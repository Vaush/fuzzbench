# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Utility functions for coverage data calculation."""

import math
import posixpath
from collections import defaultdict
import pandas as pd

from common import filestore_utils
from common import experiment_utils as exp_utils

_DEFAULT_RARE_REGION_THRESHOLD = 0


def download_json_summary(experiment_name, dst_file):
    """Downloads the json summary for |experiment_name| to |dst_file|."""
    filestore_path = exp_utils.get_filestore_path()
    src_file = posixpath.join(filestore_path, experiment_name, 'reports',
                              'covered_regions.json')
    filestore_utils.cp(src_file, dst_file)


def get_rare_region_dict(benchmark_coverage_dict,
                         threshold=_DEFAULT_RARE_REGION_THRESHOLD):
    """Returns a dictionary containing the covering fuzzers for each
    rare region, where the |threshold| defines which regions are rare."""
    region_dict = defaultdict(list)
    rare_region_dict = {}
    threshold_count = math.ceil(len(benchmark_coverage_dict) * threshold)
    if threshold_count == 0:
        threshold_count = 1
    for fuzzer in benchmark_coverage_dict:
        for region in benchmark_coverage_dict[fuzzer]:
            region_dict[region].append(fuzzer)
    for region, fuzzers in region_dict.items():
        if len(fuzzers) <= threshold_count:
            rare_region_dict[region] = fuzzers
    return rare_region_dict


def get_rare_region_cov_df(rare_region_dict, fuzzer_names):
    """Returns a DataFrame where the two columns are fuzzers and the number
    of rare regions covered."""
    fuzzers = {fuzzer_name: 0 for fuzzer_name in fuzzer_names}
    for region in rare_region_dict:
        for fuzzer in rare_region_dict[region]:
            fuzzers[fuzzer] += 1
    dict_to_transform = {'fuzzer': [], 'rare_region_covered': []}
    for fuzzer, covered_num in fuzzers.items():
        dict_to_transform['fuzzer'].append(fuzzer)
        dict_to_transform['rare_region_covered'].append(covered_num)
    return pd.DataFrame(dict_to_transform)


def get_benchmark_cov_dict(coverage_dict, benchmark):
    """Returns a dictionary to store the covered regions of each fuzzer.
    Uses a set of tuples to store the covered regions."""
    benchmark_cov_dict = {}
    for key_pair, covered_regions in coverage_dict.items():
        current_fuzzer, current_benchmark = key_pair.split()
        if current_benchmark == benchmark:
            covered_regions_in_set = set()
            for region in covered_regions:
                covered_regions_in_set.add(tuple(region))
            benchmark_cov_dict[current_fuzzer] = covered_regions_in_set
    return benchmark_cov_dict


def get_correlation_table(benchmark_coverage_dict):
    """Returns a table that shows the correlation between each two fuzzers.

    The correlation table is a square matrix where each row and column
    represents a fuzzer, and each cell contains a number showing the
    regions covered by the fuzzer of the column but not by the fuzzer
    of the row."""

    fuzzers = benchmark_coverage_dict.keys()

    correlation_values = []
    for fuzzer_in_row in fuzzers:
        row = []
        for fuzzer_in_col in fuzzers:
            correlation_value = get_unique_covered_percentage(
                benchmark_coverage_dict[fuzzer_in_row],
                benchmark_coverage_dict[fuzzer_in_col])
            row.append(correlation_value)
        correlation_values.append(row)

    return pd.DataFrame(correlation_values, index=fuzzers, columns=fuzzers)


def get_unique_covered_percentage(fuzzer_row_covered_regions,
                                  fuzzer_col_covered_regions):
    """Returns the number of regions covered by the fuzzer of the column
    but not by the fuzzer of the row."""

    unique_region_num = 0
    for region in fuzzer_col_covered_regions:
        if region not in fuzzer_row_covered_regions:
            unique_region_num += 1
    return unique_region_num
