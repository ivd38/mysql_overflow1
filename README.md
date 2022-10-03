MySQL Cluster 8.0.30 ndbd Dbdih::execSTART_MECONF() overflow

'ndbd' - so called Data node daemon, listens on INADDR_ANY, random port number.
```
Bug details:
void Dbdih::execSTART_MECONF(Signal* signal)
{
  jamEntry();
  StartMeConf * const startMe = (StartMeConf *)&signal->theData[0];
  Uint32 nodeId = startMe->startingNodeId;
[1]  const Uint32 startWord = startMe->startWord;

  CRASH_INSERTION(7130);
  ndbrequire(nodeId == cownNodeId);
  bool v2_format = true;
  Uint32 cdata_size_in_words;
[2]  if (ndbd_send_node_bitmask_in_section(getNodeInfo(cmasterNodeId).m_version))
  {
    jam();
    ndbrequire(signal->getNoOfSections() == 1);
    SegmentedSectionPtr ptr;
    SectionHandle handle(this, signal);
    ndbrequire(handle.getSection(ptr, 0));
    ndbrequire(ptr.sz <= (sizeof(cdata)/4));
    copy(cdata, ptr);
    cdata_size_in_words = ptr.sz;
    releaseSections(handle);
  }
  else
  {
    jam();
    v2_format = false;
[3]    arrGuard(startWord + StartMeConf::DATA_SIZE, sizeof(cdata)/4);
    for(Uint32 i = 0; i < StartMeConf::DATA_SIZE; i++)
    {
[4]      cdata[startWord+i] = startMe->data[i];
    }


}

We control the contents of signal->theData buffer.
If master node is an old 7.6 version, which is still supported, check on line #2 fails and we go to line #3. 
This check can be easily bypassed if startWord is negative.
On line #4 we have nice heap overflow.

To simplify the testing, edit line #2 and disable this code path.

How to test:
1) build and install mysql cluster
2) start mysqld: 
# ./bin/mysqld_safe --defaults-file=/var/mysql/etc/my.cnf --user=mysql

3) start ndb_mgmd:
# ./bin/ndb_mgmd -f /var/mysql/etc/config.ini --nodaemon 

4) start ndbd:
# ./bin/ndbd -c 192.168.1.39 --nodaemon 

'ndbd' listens on random port, test script will query ndb_mgmd for this port automatically.

Also, you can't connect to ndbd as node 3(mysqld) if mysqld is running.

There are several ways to test this vulnerability:
1) quick way to test the bug - do not start mysqld, you can use t1.py 
2) do not stop mysqld, you can restart all services via ndbd_mgmd and send requests  during restart

```
Debug session:
```
Thread 2.1 "ndbd" received signal SIGSEGV, Segmentation fault.
[Switching to Thread 0x7ffff76dc080 (LWP 152682)]
0x000055555578a414 in Dbdih::execSTART_MECONF ()
    at /mysql/new/mysql-cluster-gpl-8.0.30/storage/ndb/src/kernel/blocks/dbdih/DbdihMain.cpp:2738
2738	      cdata[startWord+i] = startMe->data[i];
(gdb) x/1i $pc
=> 0x55555578a414 <Dbdih::execSTART_MECONF(Signal*)+276>:	mov    %ecx,0x99f78(%r12,%rdx,4)
(gdb) i r r12 rdx
r12            0x7fffd6142040      140736785031232
rdx            0xfffffff1          4294967281
(gdb) i r ecx
ecx            0xffffff02          -254
(gdb)

```
