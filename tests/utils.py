def delete_folder(pth) :
    import pathlib

    for sub in pth.iterdir() :
        if sub.is_dir() :
            delete_folder(sub)
        else :
            sub.unlink()
    pth.rmdir() # if you just want to delete the dir content but not the dir itself, remove this line
