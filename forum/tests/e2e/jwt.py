import base64,hmac,hashlib,json,sys,time
SECRET=b"local-test-secret-local-test-secret-123456"
def b64(x): return base64.urlsafe_b64encode(x).rstrip(b"=").decode()
def make(role, sub=None, email=None):
    h=b64(json.dumps({"alg":"HS256","typ":"JWT"}).encode())
    p={"role":role,"iat":int(time.time()),"exp":int(time.time())+86400*30,"aud":"authenticated"}
    if sub: p["sub"]=sub
    if email: p["email"]=email
    p=b64(json.dumps(p).encode())
    s=b64(hmac.new(SECRET,f"{h}.{p}".encode(),hashlib.sha256).digest())
    return f"{h}.{p}.{s}"
if __name__=="__main__":
    print(make(*sys.argv[1:]))
