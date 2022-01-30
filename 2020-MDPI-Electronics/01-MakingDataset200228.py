## WARNING: This code is legacy code that not used now.
## This is just for archive

data_root = os.path.abspath(os.path.expanduser(SRC_DATA))
dst_base = os.path.abspath(os.path.expanduser(DST_DATA))

if IS_RESET:
    if os.path.exists(dst_base):
        shutil.rmtree(dst_base)

if TYPE is 'balanced_iid':
    cnt = [178]*6
    for label, files in get_files(data_root):
        random.shuffle(files)
        for i in range(0, CLIENTS):
            dst = os.path.join(dst_base, str(i), label)
            os.makedirs(dst, exist_ok=True) 
            for path in files[sum(cnt[:i]):sum(cnt[:i+1])]:
                shutil.copy(path, dst)
elif TYPE is 'unbalanced_iid':
    cnt = [178, 59, 118, 178, 238, 297]
    for label, files in get_files(data_root):
        random.shuffle(files)
        for i in range(0, CLIENTS):
            dst = os.path.join(dst_base, str(i), label)
            os.makedirs(dst, exist_ok=True) 
            for path in files[sum(cnt[:i]):sum(cnt[:i+1])]:
                shutil.copy(path, dst)
elif TYPE is 'balanced_noniid':
    class_div = dict()
    with os.scandir(data_root) as it:
        classes = list()
        for entry in it:
            if not entry.name.startswith('.') and entry.is_dir():
                name = os.path.basename(entry.path)
                classes.append(name)
        for _ in range(2):
            random.shuffle(classes)
            for div in classes:
                for i in range(1, CLIENTS):
                    l = class_div.get(i, set())
                    if len(l) == 6:
                        continue
                    elif div in l:
                        continue
                    l.add(div)
                    class_div[i] = l
                    break
    cnt = [178, 445, 445]
    appear = list()
    for label, files in get_files(data_root):
        random.shuffle(files)
        for i in range(0, CLIENTS):
            if i != 0:
                if label not in class_div[i]:
                    continue
            dst = os.path.join(dst_base, str(i), label)
            os.makedirs(dst, exist_ok=True)
            s = appear.count(label)
            for path in files[sum(cnt[:s]):sum(cnt[:s+1])]:
                shutil.copy(path, dst)
            appear.append(label)
elif TYPE is 'unbalanced_noniid':
    class_div = dict()
    with os.scandir(data_root) as it:
        classes = list()
        for entry in it:
            if not entry.name.startswith('.') and entry.is_dir():
                name = os.path.basename(entry.path)
                classes.append(name)
        for _ in range(2):
            random.shuffle(classes)
            for div in classes:
                for i in range(1, CLIENTS):
                    l = class_div.get(i, set())
                    if len(l) == 6:
                        continue
                    elif div in l:
                        continue
                    l.add(div)
                    class_div[i] = l
                    break
    streak = dict()
    nums = dict()
    for i in range(1, 6):
        nums[i] = [356]*i + [534]*(6-i)
        random.shuffle(nums[i])
    for label, files in get_files(data_root):
        random.shuffle(files)
        dst = os.path.join(dst_base, str(0), label)
        os.makedirs(dst, exist_ok=True)
        for path in files[0:178]:
            shutil.copy(path, dst)
        streak[label] = streak.get(label, 0) + 178
        for i in range(1, CLIENTS):
            if label not in class_div[i]:
                continue
            dst = os.path.join(dst_base, str(i), label)
            os.makedirs(dst, exist_ok=True)
            s = streak.get(label, 0)
            e = nums[i].pop()
            for path in files[s:s+e]:
                shutil.copy(path, dst)
            streak[label] = s + e
elif TYPE is 'as_is':
    for label, files in get_files(data_root):
        random.shuffle(files)
        cnt = int(len(files)*0.01)
        for i in range(0, CLIENTS):
            dst = os.path.join(dst_base, str(i), label)
            os.makedirs(dst, exist_ok=True) 
            for path in files[i*cnt:(i+1)*cnt]:
                shutil.copy(path, dst)