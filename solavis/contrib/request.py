import os
import time
import shutil
import pickle
import base64
import sqlite3
import asyncio
import aiosqlite

from multiprocessing import Queue

from solavis.core.request import RequestLoader, Request
from solavis.util.async_helper import run_in_executor

class MemoryRequestLoader(RequestLoader):
    def __init__(self):
        super().__init__()
        self.reqs = Queue()

    async def load(self):
        if not self.reqs.empty():
            return self.reqs.get()
        else:
            return None

    async def save(self, req):
        self.reqs.put(req)


class SqliteRequestLoader(RequestLoader):
    def __init__(self, dir_name):
        super().__init__()
        self.dir_name = dir_name
        
        self.save_buffer = []
        self.last_save_time = time.time()

    async def init_db(self):
        cursor = await self.connection.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='requests';")
        table_result = await cursor.fetchall()
        if table_result[0][0] == 0:
            await self.connection.execute('''CREATE TABLE requests (
                            "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                            "url" TEXT,
                            "spider_name" TEXT,
                            "method_name" TEXT,
                            "meta" TEXT
                        );''')

        await cursor.close()
        await self.connection.commit()

    async def load(self):
        ret = None

        cursor = await self.connection.execute('''
            SELECT id, url, spider_name, method_name, meta
            FROM requests
            LIMIT 1;
        ''')

        req = await cursor.fetchone()

        if req is not None:
            await self.connection.execute(f'''
                DELETE FROM requests
                WHERE id = '{req[0]}';
            ''')
            ret = Request(req[1], req[2], req[3], pickle.loads(base64.b64decode(req[4])))

        await cursor.close()
        return ret

    async def save(self, req):
        self.save_buffer.append((req.url, req.spider_name, req.method_name, bytes.decode(base64.b64encode(pickle.dumps(req.meta)))))

        if time.time() - self.last_save_time > 3:
            await self.connection.executemany(f'''
                INSERT INTO requests
                (url, spider_name, method_name, meta)
                VALUES
                (?,?,?,?);
            ''', self.save_buffer)
            await self.connection.commit()

    async def save_start_urls(self, spider):
        cursor = await self.connection.execute("SELECT count(*) FROM requests;")
        result = await cursor.fetchall()
        if result[0][0] == 0:
            for each_url in spider.start_urls:
                req = Request(each_url, spider.__class__.__name__, 'parse')
                await self.connection.execute(f'''
                    INSERT INTO requests
                    (url, spider_name, method_name, meta)
                    VALUES
                    ('{req.url}', '{req.spider_name}', '{req.method_name}', '{bytes.decode(base64.b64encode(pickle.dumps(req.meta)))}');
                ''')
        await cursor.close()
        await self.connection.commit()

    async def process_spider_open(self, spider):
        self.connection = await aiosqlite.connect(os.path.join(self.dir_name, 'solavis.db'))
        await self.init_db()
    
    async def process_spider_close(self, spider):
        await self.connection.close()
        


    