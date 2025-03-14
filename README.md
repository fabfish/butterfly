Code to accompany the papers [Learning Fast Algorithms for Linear Transforms
Using Butterfly Factorizations](https://arxiv.org/abs/1903.05895) and [Kaleidoscope: An Efficient, Learnable Representation For All Structured Linear Maps](https://openreview.net/forum?id=BkgrBgSYDS).

## Requirements

python>=3.6
pytorch>=1.8
numpy
scipy

# Installing the fast CUDA implementation of butterfly multiply:

To install:

```
python setup.py install
```

That is, use the `setup.py` file in this root directory.

An example of creating a conda environment and then installing the CUDA
butterfly multiply (h/t Nir Ailon):

```
conda create --name butterfly python=3.8 scipy pytorch=1.8.1 cudatoolkit=11.3 -c pytorch
conda install pytorch==1.8.1 torchvision==0.9.1 torchaudio==0.8.1 cudatoolkit=11.3 -c pytorch -c conda-forge
conda activate butterfly
python setup.py install
```

pip install sacred pandas ray[tune] fairseq traitlets

pip install ipykernel jinja2 nbconvert nbformat

```


qtconsole 5.1.0 requires ipykernel>=4.1, which is not installed.
notebook 6.4.0 requires ipykernel, which is not installed.
notebook 6.4.0 requires jinja2, which is not installed.
notebook 6.4.0 requires nbconvert, which is not installed.
notebook 6.4.0 requires nbformat, which is not installed.
nbclient 0.5.3 requires nbformat>=5.0, which is not installed.
jupyter 1.0.0 requires ipykernel, which is not installed.
jupyter 1.0.0 requires nbconvert, which is not installed.
ipywidgets 7.6.3 requires ipykernel>=4.5.1, which is not installed.
ipywidgets 7.6.3 requires nbformat>=4.2.0, which is not installed.
```

# Usage

2020-08-03: The new interface to butterfly C++/CUDA code is in `csrc` and
`torch_butterfly`.
It is tested in `tests/test_butterfly.py` (which also shows example usage).

The file `torch_butterfly/special.py` shows how to construct butterfly matrices
that performs FFT, inverse FFT, circulant matrix multiplication,
Hadamard transform, and torch.nn.Conv1d with circular padding. The tests in
`tests/test_special.py` show that these butterfly matrices exactly perform
those operations.

## Old interface

Note: this interface is being rewritten. Only use this if you need some feature
that's not supported in the new interface.

* The module `Butterfly` in `butterfly/butterfly.py` can be used as a drop-in
  replacement for a `nn.Linear` layer. The files in `butterfly` directory are all
  that are needed for this use.

The butterfly multiplication is written in C++ and CUDA as PyTorch extension.
To install it:

```
cd butterfly/factor_multiply
python setup.py install
cd butterfly/factor_multiply_fast
python setup.py install
```

Without the C++/CUDA version, butterfly multiplication is still usable, but is
quite slow. The variable `use_extension` in `butterfly/butterfly_multiply.py`
controls whether to use the C++/CUDA version or the pure PyTorch version.

For training, we've had better results with the Adam optimizer than SGD.

* The directory `learning_transforms` contains code to learn the transforms
  as presented in the paper. This directory is presently being developed and
  refactored.
