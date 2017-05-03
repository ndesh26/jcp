class main {
    void main(){
        int fd;
        char c = '0';
        fd = create("lhail");
        writeChar(fd, c);
        close(fd);
    }
}
