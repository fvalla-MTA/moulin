# SPDX-License-Identifier: Apache-2.0
# Copyright 2022 EPAM Systems
"""
Zephyr build generator
"""

import os.path
from typing import List
from moulin.yaml_wrapper import YamlValue
from moulin import ninja_syntax
from moulin.utils import construct_fetcher_dep_cmd


def get_builder(conf: YamlValue, name: str, build_dir: str, src_stamps: List[str],
                generator: ninja_syntax.Writer):
    """
    Return configured Zephyr builder
    """
    return ZephyrBuilder(conf, name, build_dir, src_stamps, generator)


def gen_build_rules(generator: ninja_syntax.Writer):
    """
    Generate Zephyr build rules for ninja
    """
    cmd = " && ".join([
        # Generate fetcher dependency file
        construct_fetcher_dep_cmd(),
        "cd $build_dir/zephyr",
        "west build -p auto -b $board $target",
    ])
    generator.rule("zephyr_build",
                   command=f'bash -c "{cmd}"',
                   description="Invoke Zephyr build system",
                   pool="console",
                   deps="gcc",
                   depfile=".moulin_$name.d",
                   restat=True)
    generator.newline()


class ZephyrBuilder:
    """
    ZephyrBuilder class generates Ninja rules for Zephyr build configuration
    """
    def __init__(self, conf: YamlValue, name: str, build_dir: str, src_stamps: List[str],
                 generator: ninja_syntax.Writer):
        self.conf = conf
        self.name = name
        self.generator = generator
        self.src_stamps = src_stamps
        self.build_dir = build_dir

    def gen_build(self):
        """Generate Ninja rules to build Zephyr"""
        variables = {
            "name": self.name,
            "build_dir": self.build_dir,
            "board": self.conf["board"].as_str,
            "target": self.conf["target"].as_str,
        }
        targets = self.get_targets()
        deps = list(self.src_stamps)

        self.generator.build(targets, "zephyr_build", deps, variables=variables)
        self.generator.newline()

        return targets

    def get_targets(self):
        "Return list of targets that are generated by this build"
        return [os.path.join(self.build_dir, t.as_str) for t in self.conf["target_images"]]

    def capture_state(self):
        """
        This method should capture state for reproducible builds.
        """