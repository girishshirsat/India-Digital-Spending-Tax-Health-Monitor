

def normalize_name(raw):
    row=raw.lower()
    row=row.replace("-"," ")
    row=row.replace("&", "and")
    row=" ".join(row.split())

    return row



if __name__ == "__main__":
    print(normalize_name("jammu-&-kashmir"))
    print(normalize_name("Andaman & Nicobar  Islands"))
    print(normalize_name("dadra-&-nagar-haveli-&-daman-&-diu"))