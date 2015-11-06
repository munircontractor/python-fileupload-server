# Python File Transfer Server

This is a server written in Python to transfer files from one UNIX/Linux machine to another.  

I built this partly because I had to auto-transfer files between two machines at work, but mainly because I wanted to have some fun and create a quick hack. So, I tried to do both.

The server is meant as a file transfer utility between machines that do not have FTP/SCP services running. It only allows transfer of files through POST and does not support GET requests.
Additionally, it also allows changing the owner and group of the file on the server. I added this feature to allow my colleagues to transfer files across the machines and preserve their ownership over it.

##### Usage

On the server which receives the files, use `sudo ./py-file-upload.py` to start the server. Without `sudo`, the `chmod` and `chown` function will not work, but file transfer will still work.


From the client machine, use `curl` or other utility to submit a form to the server:  
<pre>
curl -F sfname=/absolute-path/on-server/my_file.txt \
    -F "file=@/file-to-copy/test_file.txt" \
    <-F user=owner-name \>
    <-F group=group-name \>
    http://myserver-ip-address:port
</pre>

* `sfname` is the absolute path of the file on the server. Only absolute paths are allowed since I wanted the users to specify where they want to place the files.  
* `file` is the file to copy from the client. Path can be relative or absolute.
* `user` and `group` is the intended owner of the file on the server. These are optional.  
