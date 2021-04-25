files = [
['5k-Results-fasttext-cbow-Bi-Fo-cosine-cca-java.dat'],

['5k-Results-fasttext-skipgram-Bi-Fo-cosine-cca-java.dat',
'5k-Results-fasttext-skipgram-Bi-Re-cosine-cca-java.dat'],

['Results-fasttext-cbow-Bi-Fo-arcos-cca-java.dat',
'Results-fasttext-cbow-Bi-Re-arcos-cca-java.dat',
'Results-fasttext-cbow-Ne-Fo-arcos-cca-java.dat',
'Results-fasttext-cbow-Ne-Re-arcos-cca-java.dat'],

['Results-fasttext-cbow-Bi-Fo-cosine-cca-java.dat',
'Results-fasttext-cbow-Bi-Re-cosine-cca-java.dat',
'Results-fasttext-cbow-Ne-Fo-cosine-cca-java.dat',
'Results-fasttext-cbow-Ne-Re-cosine-cca-java.dat'],

['Results-fasttext-skipgram-Bi-Fo-arcos-cca-java.dat',
'Results-fasttext-skipgram-Bi-Re-arcos-cca-java.dat',
'Results-fasttext-skipgram-Ne-Fo-arcos-cca-java.dat',
'Results-fasttext-skipgram-Ne-Re-arcos-cca-java.dat'],

['Results-fasttext-skipgram-Bi-Fo-cosine-cca-java.dat',
'Results-fasttext-skipgram-Bi-Re-cosine-cca-java.dat',
'Results-fasttext-skipgram-Ne-Fo-cosine-cca-java.dat',
'Results-fasttext-skipgram-Ne-Re-cosine-cca-java.dat'],

['Results-w2v-cbow-Bi-Fo-arcos-cca-java.dat',
'Results-w2v-cbow-Bi-Re-arcos-cca-java.dat',
'Results-w2v-cbow-Ne-Fo-arcos-cca-java.dat',
'Results-w2v-cbow-Ne-Re-arcos-cca-java.dat'],

['Results-w2v-cbow-Bi-Fo-cosine-cca-java.dat',
'Results-w2v-cbow-Bi-Re-cosine-cca-java.dat',
'Results-w2v-cbow-Ne-Fo-cosine-cca-java.dat',
'Results-w2v-cbow-Ne-Re-cosine-cca-java.dat'],

['Results-w2v-skipgram-Bi-Fo-arcos-cca-java.dat',
'Results-w2v-skipgram-Bi-Re-arcos-cca-java.dat',
'Results-w2v-skipgram-Ne-Fo-arcos-cca-java.dat',
'Results-w2v-skipgram-Ne-Re-arcos-cca-java.dat'],

['Results-w2v-skipgram-Bi-Fo-cosine-cca-java.dat',
'Results-w2v-skipgram-Bi-Re-cosine-cca-java.dat',
'Results-w2v-skipgram-Ne-Fo-cosine-cca-java.dat',
'Results-w2v-skipgram-Ne-Re-cosine-cca-java.dat']

]

def main():
    with open('plotfiles.txt') as fi:
        comments = dict()
        key = None
        text = ''
        for lin in fi:
            if len(lin)>10 and lin.find(' ')<0:
                #new key.  Save old text to old key
                if key is not None:
                    comments[key] = text
                # set up for this key
                key = lin.strip()
                text = ''
            else:   # not a key.  Add line to text
                text += lin

    with open('report.htm','w') as fo:
        with open('make.gnuplots','w') as fg:
            fo.write('<html><body>\n')
            for fl in files:
                title = fl[0][:-4] # drop extension
                e1 = title.find('B')
                if e1 < 0: 
                    e1 = title.find('N')
                if e1 < 0: 
                    raise Exception('oops')
                title = title[:e1]+title[e1+6:]
                fo.write('<h1>')
                fo.write(title)
                fo.write('</h1>')
                pic1,pic2 = makeg(title,fl,fg)
                fo.write("""
                    <table><tr><td>""")
                fo.write('<img src="')
                fo.write(pic1)
                fo.write('">\n')
                fo.write('<td><img src="')
                fo.write(pic2)
                fo.write('">\n</table>')
                fo.write('<br/>\n')
                comm =  comments.get(title,None)
                if comm is not None:
                    fo.write('<par>\n%s\n</par>\n'%comm)

            fo.write('</body></html>\n')

def makeg(pname, flist, handle):
    fname = ['BINA-'+pname+'.png','RANK-'+pname+'.png']
    for j in range(2):
        handle.write('set terminal push\n')
        handle.write('set terminal pngcairo\n')
        handle.write('set output "')
        handle.write(fname[j])
        handle.write('"\n')

        for i,fna in enumerate(flist):

            if i == 0:
                handle.write('plot "')
            else:
                handle.write(', "')
            handle.write(fna)
            if j==0:
                handle.write(
                  '" using 1:2:3 with errorlines')
            else:
                handle.write(
                  '" using 1:16:17 with errorlines')
        handle.write('\n')
        handle.write('\nset output\n')
        handle.write('set terminal pop\n')

    return fname[0], fname[1]


                    
main()
