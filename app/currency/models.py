from sqlalchemy import Column, Integer, Float, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class CurrencyRate(Base):
    __tablename__ = "currency_rates"

    id = Column(Integer, primary_key=True, index=True)

    # Base currency is USD
    USD = Column(Float, nullable=False, default=1.0)

    # All other currencies
    AED = Column(Float, nullable=True)
    AFN = Column(Float, nullable=True)
    ALL = Column(Float, nullable=True)
    AMD = Column(Float, nullable=True)
    ANG = Column(Float, nullable=True)
    AOA = Column(Float, nullable=True)
    ARS = Column(Float, nullable=True)
    AUD = Column(Float, nullable=True)
    AWG = Column(Float, nullable=True)
    AZN = Column(Float, nullable=True)
    BAM = Column(Float, nullable=True)
    BBD = Column(Float, nullable=True)
    BDT = Column(Float, nullable=True)
    BGN = Column(Float, nullable=True)
    BHD = Column(Float, nullable=True)
    BIF = Column(Float, nullable=True)
    BMD = Column(Float, nullable=True)
    BND = Column(Float, nullable=True)
    BOB = Column(Float, nullable=True)
    BRL = Column(Float, nullable=True)
    BSD = Column(Float, nullable=True)
    BTN = Column(Float, nullable=True)
    BWP = Column(Float, nullable=True)
    BYN = Column(Float, nullable=True)
    BZD = Column(Float, nullable=True)
    CAD = Column(Float, nullable=True)
    CDF = Column(Float, nullable=True)
    CHF = Column(Float, nullable=True)
    CLP = Column(Float, nullable=True)
    CNY = Column(Float, nullable=True)
    COP = Column(Float, nullable=True)
    CRC = Column(Float, nullable=True)
    CUP = Column(Float, nullable=True)
    CVE = Column(Float, nullable=True)
    CZK = Column(Float, nullable=True)
    DJF = Column(Float, nullable=True)
    DKK = Column(Float, nullable=True)
    DOP = Column(Float, nullable=True)
    DZD = Column(Float, nullable=True)
    EGP = Column(Float, nullable=True)
    ERN = Column(Float, nullable=True)
    ETB = Column(Float, nullable=True)
    EUR = Column(Float, nullable=True)
    FJD = Column(Float, nullable=True)
    FKP = Column(Float, nullable=True)
    FOK = Column(Float, nullable=True)
    GBP = Column(Float, nullable=True)
    GEL = Column(Float, nullable=True)
    GGP = Column(Float, nullable=True)
    GHS = Column(Float, nullable=True)
    GIP = Column(Float, nullable=True)
    GMD = Column(Float, nullable=True)
    GNF = Column(Float, nullable=True)
    GTQ = Column(Float, nullable=True)
    GYD = Column(Float, nullable=True)
    HKD = Column(Float, nullable=True)
    HNL = Column(Float, nullable=True)
    HRK = Column(Float, nullable=True)
    HTG = Column(Float, nullable=True)
    HUF = Column(Float, nullable=True)
    IDR = Column(Float, nullable=True)
    ILS = Column(Float, nullable=True)
    IMP = Column(Float, nullable=True)
    INR = Column(Float, nullable=True)
    IQD = Column(Float, nullable=True)
    IRR = Column(Float, nullable=True)
    ISK = Column(Float, nullable=True)
    JEP = Column(Float, nullable=True)
    JMD = Column(Float, nullable=True)
    JOD = Column(Float, nullable=True)
    JPY = Column(Float, nullable=True)
    KES = Column(Float, nullable=True)
    KGS = Column(Float, nullable=True)
    KHR = Column(Float, nullable=True)
    KID = Column(Float, nullable=True)
    KMF = Column(Float, nullable=True)
    KRW = Column(Float, nullable=True)
    KWD = Column(Float, nullable=True)
    KYD = Column(Float, nullable=True)
    KZT = Column(Float, nullable=True)
    LAK = Column(Float, nullable=True)
    LBP = Column(Float, nullable=True)
    LKR = Column(Float, nullable=True)
    LRD = Column(Float, nullable=True)
    LSL = Column(Float, nullable=True)
    LYD = Column(Float, nullable=True)
    MAD = Column(Float, nullable=True)
    MDL = Column(Float, nullable=True)
    MGA = Column(Float, nullable=True)
    MKD = Column(Float, nullable=True)
    MMK = Column(Float, nullable=True)
    MNT = Column(Float, nullable=True)
    MOP = Column(Float, nullable=True)
    MRU = Column(Float, nullable=True)
    MUR = Column(Float, nullable=True)
    MVR = Column(Float, nullable=True)
    MWK = Column(Float, nullable=True)
    MXN = Column(Float, nullable=True)
    MYR = Column(Float, nullable=True)
    MZN = Column(Float, nullable=True)
    NAD = Column(Float, nullable=True)
    NGN = Column(Float, nullable=True)
    NIO = Column(Float, nullable=True)
    NOK = Column(Float, nullable=True)
    NPR = Column(Float, nullable=True)
    NZD = Column(Float, nullable=True)
    OMR = Column(Float, nullable=True)
    PAB = Column(Float, nullable=True)
    PEN = Column(Float, nullable=True)
    PGK = Column(Float, nullable=True)
    PHP = Column(Float, nullable=True)
    PKR = Column(Float, nullable=True)
    PLN = Column(Float, nullable=True)
    PYG = Column(Float, nullable=True)
    QAR = Column(Float, nullable=True)
    RON = Column(Float, nullable=True)
    RSD = Column(Float, nullable=True)
    RUB = Column(Float, nullable=True)
    RWF = Column(Float, nullable=True)
    SAR = Column(Float, nullable=True)
    SBD = Column(Float, nullable=True)
    SCR = Column(Float, nullable=True)
    SDG = Column(Float, nullable=True)
    SEK = Column(Float, nullable=True)
    SGD = Column(Float, nullable=True)
    SHP = Column(Float, nullable=True)
    SLL = Column(Float, nullable=True)
    SOS = Column(Float, nullable=True)
    SRD = Column(Float, nullable=True)
    SSP = Column(Float, nullable=True)
    STN = Column(Float, nullable=True)
    SYP = Column(Float, nullable=True)
    SZL = Column(Float, nullable=True)
    THB = Column(Float, nullable=True)
    TJS = Column(Float, nullable=True)
    TMT = Column(Float, nullable=True)
    TND = Column(Float, nullable=True)
    TOP = Column(Float, nullable=True)
    TRY = Column(Float, nullable=True)
    TTD = Column(Float, nullable=True)
    TVD = Column(Float, nullable=True)
    TWD = Column(Float, nullable=True)
    TZS = Column(Float, nullable=True)
    UAH = Column(Float, nullable=True)
    UGX = Column(Float, nullable=True)
    UYU = Column(Float, nullable=True)
    UZS = Column(Float, nullable=True)
    VES = Column(Float, nullable=True)
    VND = Column(Float, nullable=True)
    VUV = Column(Float, nullable=True)
    WST = Column(Float, nullable=True)
    XOF = Column(Float, nullable=True)
    YER = Column(Float, nullable=True)
    ZAR = Column(Float, nullable=True)
    ZMW = Column(Float, nullable=True)
    ZWL = Column(Float, nullable=True)

    # Metal Currencies
    XAU = Column(Float, nullable=True)  # Gold
    XAG = Column(Float, nullable=True)  # Silver

    # Top 50 Crypto
    BTC = Column(Float, nullable=True)     # Bitcoin
    ETH = Column(Float, nullable=True)     # Ethereum
    USDT = Column(Float, nullable=True)    # Tether
    BNB = Column(Float, nullable=True)     # BNB
    SOL = Column(Float, nullable=True)     # Solana
    USDC = Column(Float, nullable=True)    # USD Coin
    XRP = Column(Float, nullable=True)     # XRP
    TON = Column(Float, nullable=True)     # Toncoin
    DOGE = Column(Float, nullable=True)    # Dogecoin
    ADA = Column(Float, nullable=True)     # Cardano
    AVAX = Column(Float, nullable=True)    # Avalanche
    TRX = Column(Float, nullable=True)     # TRON
    LINK = Column(Float, nullable=True)    # Chainlink
    DOT = Column(Float, nullable=True)     # Polkadot
    WBTC = Column(Float, nullable=True)    # Wrapped Bitcoin
    SHIB = Column(Float, nullable=True)    # Shiba Inu
    BCH = Column(Float, nullable=True)     # Bitcoin Cash
    LTC = Column(Float, nullable=True)     # Litecoin
    ICP = Column(Float, nullable=True)     # Internet Computer
    MATIC = Column(Float, nullable=True)   # Polygon
    UNI = Column(Float, nullable=True)     # Uniswap
    ETC = Column(Float, nullable=True)     # Ethereum Classic
    XLM = Column(Float, nullable=True)     # Stellar
    APT = Column(Float, nullable=True)     # Aptos
    NEAR = Column(Float, nullable=True)    # NEAR Protocol
    OKB = Column(Float, nullable=True)     # OKB
    LDO = Column(Float, nullable=True)     # Lido DAO
    FIL = Column(Float, nullable=True)     # Filecoin
    MNT = Column(Float, nullable=True)     # Mantle
    HBAR = Column(Float, nullable=True)    # Hedera
    CRO = Column(Float, nullable=True)     # Cronos
    STX = Column(Float, nullable=True)     # Stacks
    INJ = Column(Float, nullable=True)     # Injective
    RNDR = Column(Float, nullable=True)    # Render
    IMX = Column(Float, nullable=True)     # Immutable
    ARB = Column(Float, nullable=True)     # Arbitrum
    VET = Column(Float, nullable=True)     # VeChain
    MKR = Column(Float, nullable=True)     # Maker
    AAVE = Column(Float, nullable=True)    # Aave
    KAS = Column(Float, nullable=True)     # Kaspa
    QNT = Column(Float, nullable=True)     # Quant
    GRT = Column(Float, nullable=True)     # The Graph
    ALGO = Column(Float, nullable=True)    # Algorand
    OP = Column(Float, nullable=True)      # Optimism
    SAND = Column(Float, nullable=True)    # The Sandbox
    EGLD = Column(Float, nullable=True)    # MultiversX (Elrond)
    XTZ = Column(Float, nullable=True)     # Tezos
    RUNE = Column(Float, nullable=True)    # THORChain
    FTM = Column(Float, nullable=True)     # Fantom
    EOS = Column(Float, nullable=True)     # EOS




    # Timestamp
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
