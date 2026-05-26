set_ = ['asdf 3 3\nF','33js\nj  ']
sizes = []
for item in set_:
    for i in item.split("\n"):
        sizes.append(len(i))

max_size = max(sizes)
print(max_size)