from readmegen import ReadmeGenerator

if __name__ == "__main__":



    dirs = ["img", "description"]

    lists = [[['./readmegen/readmegen.py'],
                        './img/graph.png']]

    rgen = ReadmeGenerator(lists)
    rgen.generate('./readmegen/')
             
