"""reading and writing files handling different possible encodings

Example:
```
>>> rwfile = ReadWriteFile()
>>> input_path = 'path/to/input_file'
>>> result = rwfile.readAnything(input_path)
>>> print(f'encoding: "{rwfile.encoding}", bom: "{rwfile.bom}")
>>> output_string = result + 'new text\n'
>>> output_path = 'path/to/output_file'
>>> rwfile.writeAnything(output_path, output_string)
```

The "bom mark" is sometimes/especially the case with the ini files of the Dragon program

### using this with configparser:
    ```
    rwfile = ReadWriteFile()
    self.config_text = rwfile.readAnything(filepath)
    Config = configparser.ConfigParser()
    Config.read_string(self.config_text)
    ```

Quintijn Hoogenboom, 2018, March 2022/November 2023
"""
#pylint:disable=R0912, C0209
import os
import sys

class ReadWriteFile:
    """instance to read any text file and/or and write text into same or new file
    
    collect encoding and bom mark (byte order mark, sometimes in Windows)
    
    `encodings` and `encoding` can be overridden at creation of an instance.
    `encodings` must then be a list of possible encodings
    `encoding` is then 
    when `encoding` is a str, `encodings` is set to a list only containing this encoding
    
    the default `encodings` are: `['ascii', 'utf-8', 'cp1252',  'latin-1']`
    
    a file can be read via this class, and write back another string, using the same encoding and bom mark
    
    When the encoding is 'ascii' and at write time, non ascii characters are present, care is taken to
    encode the output to another encoding, most often (default) 'utf-8'.
    """
    def __init__(self, encodings=None):
        self.input_path = ''
        self.bom = ''
        self.text = ''
        self.rawText = b''
        if isinstance(encodings, str):
            raise TypeError(f'readwritefile, variable "encodings" should be a list, not "{encodings}" (type: {type(encodings)}))')
        self.encodings = encodings or ['ascii', 'utf-8', 'cp1252',  'latin-1']
        self.encoding = self.encodings[0]

    
    def readAnything(self, input_path, encoding=None):
        """take any file and decode to a str
        
        works best if encoding is NOT given.
    
        Try subsequently the encodings, unless overriden by
        the encoding variable (str of list of strings)
        """
        self.input_path = input_path
        if encoding:
            if isinstance(encoding, str):
                self.encodings = [encoding]
            elif isinstance(encoding, (list, tuple)):
                self.encodings = list(encoding)
            else:
                raise ValueError(f'readwritefile, readAnything: invalid input variable "encoding": {encoding}')
            self.encoding = self.encodings[0]
            
        if not os.path.isfile(self.input_path):
            raise OSError(f'readwritefile, readAnything: not a file: "{self.input_path}"')
        
        with open(self.input_path, mode='rb') as file: # b is important -> binary
            self.rawText = file.read()
        tRaw = fixCrLf(self.rawText)
        #
        for codingscheme in self.encodings:
            result = DecodeEncode(tRaw, codingscheme)
            if not result is False:
                if codingscheme in ('cp1252', 'latin-1'):
                    pass
                if result and ord(result[0]) == 65279:  # BOM, remove
                    result = result[1:]
                    self.bom = tRaw[0:3]
                self.text = result
                self.encoding = codingscheme
                return result
        print(f'readAnything: no valid encoding found for file: {input_path}')
        self.text = ''
        return ''
    
    def writeAnything(self, filepath, content, encoding=None, errors=None):
        """write str or list of strings to file

        Take the given `encoding` or the `encoding` of the input (`self.encoding`) or
        the first from `self.encodings` (mostly 'ascii') (new file),
        and take the bom of the input or ''
        
        Then follow this encoding, but in case of 'ascii' and errors, use if possible,
        the next encoding in `self.encodings`, probably 'utf-8'.

        If they all fail, use by default errors='xmlcharrefreplace' in order
        to output all character in html format.
        errors can also be 'ignore' or 'replace'
        Note: with 'utf-8' as second encoding, there should be no errors!
        """
        errors = errors or 'strict'
        # if encoding:
        #     if isinstance(encoding, str):
        #         self.encoding = encoding
        #     elif isinstance(encoding, (list, tuple)):
        #         self.encodings = encoding
        #         self.encoding = encoding[0]
        #     else:
                # raise TypeError('readwritefile, writeAnything: unexpected type of encoding: {encoding} (type: {type(encoding)})')
        # errors = errors or 'xmlcharrefreplace'
        assert errors in ('strict', 'ignore', 'replace', 'xmlcharrefreplace')
        if isinstance(content, (list, tuple)):
            content = '\n'.join(content)
    
        if not isinstance(content, str):
            raise TypeError("writeAnything, content should be str, not %s (%s)"% (type(content), filepath))

        if not encoding and len(self.encodings) == 1:
            encoding = self.encodings[0]

        if encoding:
            try:
                tRaw = content.encode(encoding=encoding, errors=errors)
            except Exception as exc:
                msg = 'readwritefile.writeAnything, cannot encode string to raw string for writing to file %s (encoding: %s)'% (filepath, encoding)
                msg += '\nexc: %s'% repr(exc)
                raise UnicodeEncodeError(msg) from exc
       
        else:
            for enc in self.encodings:

                try:
                    tRaw = content.encode(encoding=enc)
                except UnicodeEncodeError as exc:
                    if enc == self.encodings[-1]:
                        if errors:
                            tRaw = content.encode(encoding=enc, errors=errors)
                        else:
                            message = ['readwritefile.writeAnything, cannot encode string to raw string for writing to file %s (encodings: %s)'%(filepath, self.encodings),
                                       '\tconsider to add "errors=ignore", or "errors=xmlcharrefreplace" to the call']
                            raise UnicodeEncodeError('\n'.join(message)) from exc
            
        if sys.platform == 'win32':
            tRaw = tRaw.replace(b'\n', b'\r\n')
            tRaw = tRaw.replace(b'\r\r\n', b'\r\n')
            
        if self.bom:
            # print('add bom for tRaw')
            tRaw = self.bom + tRaw 
        with open(str(filepath), 'wb') as out:  
        # what difference does a bytearray make? (QH)
            out.write(bytearray(tRaw))
    readFile = readAnything
    writeFile = writeAnything
    
### direct callable functions, in case no read and write with same bom and encodings is needed:
def readFile(filepath, encoding=None):
    """direct function, returns the str contents of any file type
    
    if no other parameters are needed, you can bypass the call to ReadWriteFile
    """
    rwfile = ReadWriteFile()
    contents = rwfile.readAnything(filepath, encoding=encoding)
    return contents


  # def writeAnything(self, filepath, content, encoding=None, errors=None):
def writeFile(filepath, content, encoding=None, errors=None):
    """direct function, returns the str contents of any file type
    
    if no other parameters are needed, you can bypass the call to ReadWriteFile
    """
    rwfile = ReadWriteFile()
    rwfile.writeAnything(filepath, content, encoding=encoding, errors=errors)


readAnything = readFile
writeAnything = writeFile

def fixCrLf(tRaw):
    """replace crlf into lf
    """
    if b'\r\r\n' in tRaw:
        print('readAnything, fixCrLf: fix crcrlf')
        tRaw = tRaw.replace(b'\r\r\n', b'\r\n')
    if b'\r' in tRaw:
        # print 'readAnything, self.fixCrLf, remove cr'
        tRaw = tRaw.replace(b'\r', b'')
    return tRaw
    
def DecodeEncode(tRaw, filetype):
    """return the decoded string or False
    
    used by readAnything, also see testreadanything in miscqh/test scripts
    """
    try:
        tDecoded = tRaw.decode(filetype)
    except UnicodeDecodeError:
        return False
    encodedAgain = tDecoded.encode(filetype)
    if encodedAgain == tRaw:
        return tDecoded
    return False

# if __name__ == '__main__':
    ## testing in test_readwritefile, PyTest directory
