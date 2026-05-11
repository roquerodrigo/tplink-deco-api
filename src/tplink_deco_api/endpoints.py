_PLAIN_ENDPOINTS: frozenset[str] = frozenset(
    {
        "/login?form=auth",
        "/login?form=keys",
        "/login?form=check_factory_default",
        "/login?form=default_info",
        "/admin/system?form=envar",
        "/admin/system?form=sysmode",
        "/admin/cloud?form=firmware",
        "/admin/isp?form=isp_upgrade",
        "/admin/firmware?form=config_multipart",
        "/admin/log_export?form=save_log",
    }
)


def is_plain(path_with_form: str) -> bool:
    return path_with_form in _PLAIN_ENDPOINTS


def login_url(host: str, form: str) -> str:
    return f"http://{host}/cgi-bin/luci/;stok=/login?form={form}"


def admin_url(host: str, stok: str, path: str, form: str) -> str:
    return f"http://{host}/cgi-bin/luci/;stok={stok}/{path}?form={form}"
