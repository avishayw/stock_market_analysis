import json

GOOGLE_APPLICATION_CREDENTIALS='d5d85ac4184033ed8d663bdb3eaa1e42e04129ab'
credentials_dict = {
    "type": "service_account",
  "project_id": "avish-analysis",
  "private_key_id": "d5d85ac4184033ed8d663bdb3eaa1e42e04129ab",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDL4ID7qh93bfn1\nfwjsxws0uIrGPbKEBoZwNa8qEI37ynhI/YhMIDBwQuLF2JC/7stT4cONEDgWiHM2\nKLIt8/CVwkC2EwCxHI+JkzdfelkKA7ZSrBtI4mEwoU9pQ/fUI7dTio5NX1PZCtDj\nP9Xci/ZvD0AXKf31SYswlCEINzlvBoHdUjA0WtSo13NEqPsOqi2NqwlTarH9HutV\nydK/fEpZtXXujLD8Ru4CElYjbfgIotJuyPXvMJZ3l0BNdcZQzL9ataJq3Fs2U1Li\n4MOOL7m+Sxu7XjNn1u9wai+YYWr2knTnHt8D41hzDHMYzPjI0Mx44Kh/VnFaXqol\n/mylmCRxAgMBAAECggEAHQhvvcb0e7Cy3ZG1XuiacSvNgV0UYKZAO1b9xo78dSyY\nVAacxAB6fWYc/qEwPdDe7idSjnJOlnDgfUgu1YntSxpSVkte+BnR2/zVsBhPeTRd\noKjHKuon/oGeOiaWcoSSjQhIav7GBTy70fzLcwCQe7DPhuzxMB7Evkp96LpaiLOC\neqHxZ1p70xbnm+nGuqNrgX08k7c7oZ4nLhhEKYP4KYj5qL3DLss++QXF3LG+cvEa\ngK+OO7ndJa7vjWOPuAt0A1XQimS+CChzxLhlbx6O3+uWo1TbFh3b1EeHYqvhxWy/\nDfRDM0XXsZJMW9qB4Im8RYt4EFtcCFwLlv+4uBdLVQKBgQD4ltXdNMwPpOepjyop\nq6OkqHU3igEt1OeBZchqz/PDt+5/cBnig+FqfmH5f9viVqCvxdtUyH8a5XizS0X9\nsRvjyafxlcFg5+rOBQMFeLWZhSgYldALsaBJ1A6kWAQhSV3FuDG6X+/qkcWwiS2V\nxBNMEqi8NQXDTHCJQ6NZLNiO9QKBgQDR9G/bLLYGONYn3lCWTegvoEAt8KuNTyce\ncUyzsn9PsiD00JOvDeE80bboO4nTBVxVpRRc/+5/fDNEly2Q0+LOgHvD2YHNXxDV\nUKFGazluhETy5X31tQWRmnuF7KkQxxs6xUGVQScWleCsWh+d9wdj576YiyYTq7bD\nBf4ta0QaDQKBgAycsnsHm7bLeglrPwtgLuxCs7e+o7Ksk5ZIELQCmu56HXqPuHB6\nmmwpv1TGPOSt2ncwhaE2juRRch8+mW12l+ClsYSbQXVmLs6HCJE1f5krXU5qA2Uk\nfOph/OAvqv35V+2ZG8TF60kuXiZHv21Sxlvcsnzh/8nZzffY26fBk7clAoGBALzX\nAKzAAFCEWoqteQpXtFjx6AfqCkMlSGgnO/f8ummyK9ZGrC6ta0NK1Rr4QjTdA3m8\n6x3izF86FNrCpyc2jS9zfN5hClDwCrHyvbwawSNYMLPQGoUfdozJyARjIoWGsEUi\nGqTmXwP/dn9O6FUqVSlUzadisLLMpauv/jhX3H8ZAoGBAOhwczpzkAwiCprP+kav\nxk0sJCoHFdUMRR8Z4Pmd6DMTAyBSdCiZEPYldxKwnX5INNqRX82v/yUo0h/eV0fA\nDOxbk1m2UXsNfWnCcqph6b7AaNx66RULKdn2odYsBxf/lDjDgT5O9GQJf9NIqo0q\nonlHoXs+R5aWJxkw4WvIR/Nu\n-----END PRIVATE KEY-----\n",
  "client_email": "777739768694-compute@developer.gserviceaccount.com",
  "client_id": "100454880964623753606",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/777739768694-compute%40developer.gserviceaccount.com"
}


def save_credentials_to_file(filename):
    with open(filename, 'w') as f:
        json.dump(credentials_dict, f)
    return filename