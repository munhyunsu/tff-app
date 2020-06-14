#### Preparation

1. Create venv with copies option for creating non-syslink python3
```bash
python3 -m venv --copies ./venv
```

2. Set [capabilities](https://www.man7.org/linux/man-pages/man7/capabilities.7.html)

  - This does not require setuid / setgid

```bash
setcap cap_net_raw,cap_net_admin=ep ./python3
getcap ./python3
```
