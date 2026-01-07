import os
from pathlib import Path
from typing import Dict, List, Union

import resend
import yaml

from .schemas import EmailParams, Mailer


class Resend:
    _cfg: Dict[str,Mailer] | None = None
    def __init__(self):


        resend.api_key = os.getenv("RESEND_API_KEY","re_8uzzKAoD_Q9FLfkwZW4qWP4STtuF63Ky5")
        if not Resend._cfg:
            current_path = Path(__file__).parent
            with open(f"{current_path}/config.yaml") as f:
                tmp = yaml.safe_load(f.read()).get("mailers",[])
                Resend._cfg = {}
                for item in tmp:
                    Resend._cfg[item.get("name")] = Mailer(**item)


    def mailer_send(self,mailer:str,to:Union[str|List[str]], subject:str,body:str,attachments = None) -> bool:
        mailer = Resend._cfg.get(mailer,None)
        if not mailer:
            return False
        email = EmailParams(**{
            "from":mailer.from_,
            "to":[to] if isinstance(to,str) else to,
            "subject":subject,
            "html":body,
            "attachments":attachments if attachments is not None else []
        })
        params: resend.Emails.SendParams = email.model_dump(by_alias=True)


        email = resend.Emails.send(params)
        if email:
            return True

        return False