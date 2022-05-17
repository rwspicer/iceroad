"""
Co-Registration
---------------

Co-registration tools

"""
from arosics import COREG_LOCAL


def coregister_local(
        reference, target, out, 
        reference_band, target_band, ws = 256, max_shift = 5,
        align_grids = True, max_iter = 1000
    ):
    """Wrapper around the arosics.COREG_LOCAL process with some basic 
    options, for full capabilities of arosics.COREG_LOCAL you should call
    that yourself.

    see https://danschef.git-pages.gfz-potsdam.de/arosics/doc/arosics.html#module-arosics.CoReg_local

    `target` image is co-registed to `reference` image and saved as `out` image
    as geotiff

    Parameters
    ----------
    reference: path
        reference image 
    target: path
        target image
    out: path
        out put image (works best as full path, if it's just a name it
        will be saved in the same directory as the reference image)
    reference_band: int
        Band # to use for the reference image 
    target_band: int
        Band # to use for the target image 
    ws: int, default 246
        window size for the matching process
    max_shift: int, default 5
        max shift for target image in pixels
    aligin_grids: bool, default True
        if True, aligns the input coordinate grid to the reference
    max_iter: int, default 100
        maximum iterations for matching process

    Returns
    -------
    arosics.COREG_LOCAL

    """
    crl = COREG_LOCAL(
        reference, target, 
        max_iter = max_iter, 
        r_b4match=reference_band, s_b4match=target_band,
        path_out = out,
        align_grids=align_grids,
        fmt_out='gtiff',
        max_shift=max_shift,
        window_size =(ws,ws),
        grid_res= 200,
        # CPUs=8
        )
    # print('starting')
    crl.correct_shifts()

    return crl
