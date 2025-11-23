from .BaseDataModel import BaseDataModel
from .db_schemas import Asset
from .enums.DataBaseEnum import DataBaseEnum
from bson import ObjectId  # pyright: ignore[reportMissingImports]
from sqlalchemy import select

class AssetModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.db_client = db_client
        # self.collection = self.db_clinet[DataBaseEnum.COLLECTION_ASSET_NAME.value]

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        # await instance.init_collection()
        return instance
    
    # async def init_collection(self):
    #     all_collection = await self.db_clinet.list_collection_names()
    #     if DataBaseEnum.COLLECTION_ASSET_NAME.value not in all_collection:
    #         self.collection  = self.db_clinet[DataBaseEnum.COLLECTION_ASSET_NAME.value]
    #         indexs = Asset.get_indexes()
    #         for index in indexs:
    #             await self.collection.create_index(
    #                 index["key"],
    #                 name=index["name"],
    #                 unique=index["unique"]
    #             )

    async def create_asset(self, asset: Asset):
        async with self.db_client() as session:
            async with session.begin():
                session.add(asset)
            await session.commit()
            await session.refresh(asset)
        return asset

        # result = await self.collection.insert_one(asset.dict(by_alias=True, exclude_unset=True))

        # asset.asset_id = result.inserted_id

        # return asset
    
    async def get_all_project_assets(self, asset_project_id: str , asset_type: str):
        async with self.db_client() as session:
            stmt = select(Asset).where(
                Asset.asset_project_id == asset_project_id , 
                Asset.asset_type == asset_type
            )
            results = await session.execute(stmt)
            records = results.scalars().all()
        return records
        
        # records =  await self.collection.find(
        #     {
        #         "asset_project_id": ObjectId(asset_project_id) if isinstance(asset_project_id, str) else asset_project_id,
        #         "asset_type" : asset_type
        #     }
        # ).to_list(length=None)
        # return [
        #     Asset(**record)
        #     for record in records
        # ]
    
    async def get_asset_record(self, asset_project_id: str, asset_name: str):
        async with self.db_client() as session:
            stmt = select(Asset).where(
                Asset.asset_project_id == asset_project_id , 
                Asset.asset_name == asset_name
            )

            result = await session.execute(stmt)
            record = result.scalar_one_or_none()
        return record

        # record = await self.collection.find_one(
        #     {
        #         "asset_project_id": ObjectId(asset_project_id) if isinstance(asset_project_id, str) else asset_project_id,
        #         "asset_name" : asset_name
        #     }
        # )
        # if record:
        #     return Asset(**record)
        # else:
        #     return None








