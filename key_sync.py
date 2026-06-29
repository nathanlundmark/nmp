import rsa



org = ("127.0.0.1", 12300)
def set_org(org_passed):
    global org
    org = org_passed

def get_org():
    return org

def get_rsa_keys():
    with open("priv.pem", "rb") as f:
        priv_key = rsa.PrivateKey.load_pkcs1(f.read())
    with open("pub.pem", "rb") as f:
        pub_key = rsa.PublicKey.load_pkcs1(f.read())

    return pub_key, priv_key


def new_rsa_keys():
    pub, priv = rsa.newkeys(2048)

    with open("pub.pem", "wb") as f:
        f.write(pub.save_pkcs1())
    with open("priv.pem", "wb") as f:
        f.write(priv.save_pkcs1())
