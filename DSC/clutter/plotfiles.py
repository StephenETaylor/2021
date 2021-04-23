files = [
['5k-Results-fasttext-cbow-Bi-Fo-cca-java.dat'
,'5k-Results-fasttext-cbow-Bi-Re-cca-java.dat'],[
'5k-Results-fasttext-skipgram-Bi-Fo-cca-java.dat'
,'5k-Results-fasttext-skipgram-Bi-Re-cca-java.dat'],[
'Results-fasttext-cbow-Bi-Fo-cca-java.dat'
,'Results-fasttext-cbow-Bi-Re-cca-java.dat'
,'Results-fasttext-cbow-Ne-Fo-cca-java.dat'
,'Results-fasttext-cbow-Ne-Re-cca-java.dat'],[
'Results-fasttext-skipgram-Bi-Fo-cca-java.dat'
,'Results-fasttext-skipgram-Bi-Re-cca-java.dat'
,'Results-fasttext-skipgram-Ne-Fo-cca-java.dat'
,'Results-fasttext-skipgram-Ne-Re-cca-java.dat'],[
'Results-w2v-cbow-Bi-Fo-cca-java.dat'
,'Results-w2v-cbow-Bi-Re-cca-java.dat'
,'Results-w2v-cbow-Ne-Fo-cca-java.dat'
,'Results-w2v-cbow-Ne-Re-cca-java.dat'],[
'Results-w2v-skipgram-Bi-Fo-cca-java.dat'
,'Results-w2v-skipgram-Bi-Re-cca-java.dat'
,'Results-w2v-skipgram-Ne-Fo-cca-java.dat'
,'Results-w2v-skipgram-Ne-Re-cca-java.dat']]

def main():
    with open('report.htm','w') as fo:
        with open('make.gnuplots','w') as fg:
            fo.write('<html><body>\n')
            for fl in files:
                title = fl[0]
                e1 = title.find('B')
                if e1 < 0: raise Exception('oops')
                title = title[:e1-1]
                fo.write('<h1>')
                fo.write(title)
                fo.write('</h1>')
                pic = makeg(title,fl,fg)
                fo.write('<img src="')
                fo.write(pic)
                fo.write('">\n')
                fo.write('<br/>\n')
            fo.write('</body></html>\n')

def makeg(pname, flist, handle):
    fname = pname+'.png'
    handle.write('set terminal push\n')
    handle.write('set terminal pngcairo\n')
    handle.write('set output "')
    handle.write(fname)
    handle.write('"\n')

    for i,fna in enumerate(flist):

        if i == 0:
            handle.write('plot "')
        else:
            handle.write(', "')
        handle.write(fna)
        handle.write('" using 1:2:3 with errorbars, "" with lines')
    handle.write('\n')
    handle.write('\nset output\n')
    handle.write('set terminal pop\n')

    return fname


                    
main()
