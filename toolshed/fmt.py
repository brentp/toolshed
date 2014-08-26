import re

def fmt2header(fmt):
    """
    Turn a python format string into a usable header:
    >>> fmt = "{chrom}\t{start:d}\t{end:d}\t{pvalue:.4g}"
    >>> fmt2header(fmt)
    'chrom  start       end pvalue'
    >>> fmt.format(chrom='chr1', start=1234, end=3456, pvalue=0.01232432)
    'chr1  1234       3456 0.01232'
    """
    return re.sub("{|(?:\:.+?)?}", "", fmt)

if __name__ == "__main__":
    import doctest
    print(doctest.testmod())
