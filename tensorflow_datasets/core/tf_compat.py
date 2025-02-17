# coding=utf-8
# Copyright 2022 The TensorFlow Datasets Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""TensorFlow compatibility utilities."""

# pylint: disable=g-import-not-at-top,g-direct-tensorflow-import

import distutils.version
import functools
import os
from typing import Optional

MIN_TF_VERSION = "2.1.0"

_ensure_tf_version_called = False


# Ensure TensorFlow version is sufficiently recent. This needs to happen after
# TensorFlow was imported, as it is referenced.
def ensure_tf_version(tf):  # pylint: disable=g-statement-before-imports
  """Ensures TensorFlow version is sufficient.

  Args:
    tf: Tensorflow module.

  Raises:
    ImportError: if tensorflow version is inadequate.
  """
  # Only check the first time.
  global _ensure_tf_version_called
  if _ensure_tf_version_called:
    return
  _ensure_tf_version_called = True

  tf_version = distutils.version.LooseVersion(tf.__version__)
  min_tf_version = distutils.version.LooseVersion(MIN_TF_VERSION)
  if tf_version < min_tf_version:
    raise ImportError(
        "This version of TensorFlow Datasets requires TensorFlow "
        f"version >= {MIN_TF_VERSION}; Detected an installation of version "
        f"{tf.__version__}. Please upgrade TensorFlow to proceed.")


def is_dataset(ds):
  """Whether ds is a Dataset. Compatible across TF versions."""
  import tensorflow as tf  # pylint: disable=import-outside-toplevel
  return isinstance(ds, (tf.data.Dataset, tf.compat.v1.data.Dataset))


def get_single_element(ds):
  """Calls `tf.data.Dataset.get_single_element`."""
  import tensorflow as tf  # pylint: disable=import-outside-toplevel
  if hasattr(ds, "get_single_element"):  # tf 2.6 and above
    return ds.get_single_element()
  else:
    return tf.data.experimental.get_single_element(ds)


def _get_option_deterministic_field() -> str:
  import tensorflow as tf  # pylint: disable=import-outside-toplevel
  if hasattr(tf.data.Options(), "deterministic"):
    return "deterministic"
  return "experimental_deterministic"


def get_option_deterministic(options) -> Optional[bool]:
  """Returns the option whether the output should be in deterministic order."""
  return getattr(options, _get_option_deterministic_field())


def set_option_deterministic(options, value: bool) -> None:
  setattr(options, _get_option_deterministic_field(), value)


def _make_pathlike_fn(fn, nb_path_arg=1):
  """Wrap the function in a PathLike-compatible function."""

  @functools.wraps(fn)
  def new_fn(*args, **kwargs):
    # Normalize PathLike objects
    args = tuple(os.fspath(arg) for arg in args[:nb_path_arg])
    return fn(*args, **kwargs)

  return new_fn
