# import math
import unittest

import numpy as np
from scipy import linalg as la

import torch
import torch_butterfly


class ButterflySpecialTest(unittest.TestCase):

    def test_fft(self):
        batch_size = 10
        n = 16
        for normalized in [False, True]:
            for br_first in [True, False]:
                input = torch.randn(batch_size, n, dtype=torch.complex64)
                b = torch_butterfly.special.fft(n, normalized=normalized, br_first=br_first)
                out = b(input)
                out_torch = torch.view_as_complex(torch.fft(torch.view_as_real(input),
                                                            signal_ndim=1, normalized=normalized))
                self.assertTrue(torch.allclose(out, out_torch))

    def test_ifft(self):
        batch_size = 10
        n = 16
        for normalized in [False, True]:
            for br_first in [True, False]:
                input = torch.randn(batch_size, n, dtype=torch.complex64)
                b = torch_butterfly.special.ifft(n, normalized=normalized, br_first=br_first)
                out = b(input)
                out_torch = torch.view_as_complex(torch.ifft(torch.view_as_real(input),
                                                             signal_ndim=1, normalized=normalized))
                self.assertTrue(torch.allclose(out, out_torch))

    def test_circulant(self):
        batch_size = 10
        n = 13
        col = torch.randn(n, dtype=torch.complex64)
        C = la.circulant(col.numpy())
        input = torch.randn(batch_size, n, dtype=torch.complex64)
        out_torch = torch.tensor(input.detach().numpy() @ C.T)
        out_np = torch.tensor(np.fft.ifft(np.fft.fft(input.numpy()) * np.fft.fft(col.numpy())),
                              dtype=torch.complex64)
        self.assertTrue(torch.allclose(out_torch, out_np))
        for separate_diagonal in [True, False]:
            b = torch_butterfly.special.circulant(col, transposed=False,
                                                  separate_diagonal=separate_diagonal)
            out = b(input)
            self.assertTrue(torch.allclose(out, out_torch))

        row = torch.randn(n, dtype=torch.complex64)
        C = la.circulant(row.numpy()).T
        input = torch.randn(batch_size, n, dtype=torch.complex64)
        out_torch = torch.tensor(input.detach().numpy() @ C.T)
        # row is the reverse of col, except the 0-th element stays put
        # This corresponds to the same reversal in the frequency domain.
        # https://en.wikipedia.org/wiki/Discrete_Fourier_transform#Time_and_frequency_reversal
        row_f = np.fft.fft(row.numpy())
        row_f_reversed = np.hstack((row_f[:1], row_f[1:][::-1]))
        out_np = torch.tensor(np.fft.ifft(np.fft.fft(input.numpy())
                                          * row_f_reversed), dtype=torch.complex64)
        self.assertTrue(torch.allclose(out_torch, out_np))
        for separate_diagonal in [True, False]:
            b = torch_butterfly.special.circulant(row, transposed=True,
                                                  separate_diagonal=separate_diagonal)
            out = b(input)
            self.assertTrue(torch.allclose(out, out_torch))


if __name__ == "__main__":
    unittest.main()
