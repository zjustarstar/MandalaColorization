import time
import os
import recolor_main as rm
import pdf_reader as pr


def param_checker(params):
    pdffile = params['recolor_targetpdf']
    if not os.path.exists(pdffile):
        print("target file :{0}  doesn't exist".format(pdffile))
        return False

    # recolor by transfer
    if params['recolor_by_transfer']:
        transfer_file = params['recolor_transfer_file']
        if not os.path.exists(transfer_file):
            print("transfer file:{0} doesn't exist".format(transfer_file))
            return False
    # transfer by color theme
    else:
        if not os.path.exists('ColorTheme.xlsx'):
            print("color theme file:ColorTheme.xlsx doesn't exist")
            return False

    # create output path
    output_path = params['output_path'] = "result"
    if not os.path.exists(output_path):
        os.mkdir(output_path)

    return True


if __name__ == "__main__":
    params = dict()
    # Ture: recolor by transferring another image color, False: recolor by color theme
    params['recolor_by_transfer'] = False
    params['recolor_transfer_file'] = "./transfer/7.png"
    # how many color will be extracted from the transfer file
    params['recolor_transfer_k'] = 30
    # recolor by color theme: read color theme from excel file
    params['recolor_colortheme_file'] = 'ColorTheme.xlsx'
    # path for saving recolored image. will auto-created if this fold does not exist.
    params['output_path'] = "result"
    # pdf file for recoloring
    params['recolor_targetpdf'] = "./testpdf/zzx_2023_09_15_08_29origin.pdf"

    # check validity of params
    if not param_checker(params):
        exit(0)

    # temporarily convert pdf file to png file
    print("is reading pdf file...")
    pngimg_2k = pr.pdf2image_2k(params['recolor_targetpdf'])

    # pngimg_2k = "./testimg/60af5ca46ebcf900012e6162.png"

    # entry of recolor processing
    start_time = time.time()
    rm.colorization_main(pngimg_2k, params)
    end_time = time.time()
    time1 = round(end_time - start_time)
    print("colorization", time1, "s")

    # remove temporary png image based on pdf file
    if os.path.exists(pngimg_2k):
        os.remove(pngimg_2k)






