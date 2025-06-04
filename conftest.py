import os
import pytest

@pytest.fixture(autouse=True)
def set_correct_paths():
    original_dir = os.getcwd()
    os.chdir(os.path.join(original_dir, "image"))
    yield
    os.chdir(original_dir)
