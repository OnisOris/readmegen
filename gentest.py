from readmegen import ReadmeGenerator

if __name__ == "__main__":
    dirs = ["img", "description"]
    lists = [[['./readmegen/readmegen.py', './readmegen/functions.py'],
                        './img/readmegen.png']]
    rgen = ReadmeGenerator(lists)
    rgen.generate('./readmegen/')
     
