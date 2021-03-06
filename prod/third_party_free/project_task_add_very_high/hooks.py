# Copyright 2017-2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def uninstall_hook(cr, registry):  # pragma: no cover
    # Convert priority from High and Very High to Normal
    # to avoid inconsistency after the module is uninstalled
    cr.execute(
        "UPDATE project_task SET priority = '1' "
        "WHERE priority like '2' or priority like '3'"
    )
