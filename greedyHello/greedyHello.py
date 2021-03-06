from iconservice import *

TAG = 'Scrooge'


class Scrooge(IconScoreBase):
    _CONTRIBUTOR_ICX = "contributor_icx"
    _CONTRIBUTOR_VALUE = "contributor_value"
    _CONTRIBUTOR_LIST = "contributor_list"
    _ICX_BALANCE = "icx_balance"
    _TOKEN_BALANCE = "token_balance"

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self._ADB_contributor_list = ArrayDB(self._CONTRIBUTOR_LIST, db, value_type=Address)
        self._DDB_contributor_icx = DictDB(self._CONTRIBUTOR_ICX, db, value_type=int)
        self._DDB_contributor_token = DictDB(self._CONTRIBUTOR_VALUE, db, value_type=int)
        self._VDB_icx_balance = VarDB(self._ICX_BALANCE, db, value_type=int)
        self._VDB_token_balance = VarDB(self._TOKEN_BALANCE, db, value_type=int)

    def on_install(self) -> None:
        super().on_install()

    def on_update(self) -> None:
        super().on_update()

    @external
    def tokenFallback(self, _from: Address, _value: int, _data: bytes):
        if self.msg.sender not in self._ADB_contributor_list:
            self._ADB_contributor_list.put(self.msg.sender)

        self._DDB_contributor_token[self.msg.sender] += _value
        self._VDB_token_balance.set(self._VDB_token_balance.get() + _value)

    @payable
    def fallback(self) -> None:
        if self.msg.sender not in self._ADB_contributor_list:
            self._ADB_contributor_list.put(self.msg.sender)

        self._DDB_contributor_icx[self.msg.sender] += self.msg.value
        self._VDB_icx_balance.set(self._VDB_token_balance.get() + self.msg.value)