#ifdef _WIN32
#include <winsock2.h>
#pragma comment(lib, "ws2_32.lib")
#endif

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
//#include <arpa/inet.h>
#include <ws2tcpip.h>
#define MAX_BUFFER_SIZE 1024
#define SERVER_PORT 8888

int main() {
    #ifdef _WIN32
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        perror("Không thể khởi động Winsock");
        exit(1);
    }
    #endif

    int sockfd;
    struct sockaddr_in server_addr, client_addr;
    char buffer[MAX_BUFFER_SIZE];

    // Tạo socket
    sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) {
        perror("Không thể tạo socket");
        exit(1);
    }

    // Khởi tạo địa chỉ server
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(SERVER_PORT);
    server_addr.sin_addr.s_addr = INADDR_ANY;

    // Gắn địa chỉ server với socket
    if (bind(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("Lỗi khi gắn địa chỉ với socket");
        exit(1);
    }

    printf("Server is listening on %d...\n", SERVER_PORT);

    while (1) {
        socklen_t client_len = sizeof(client_addr);

        // Nhận dữ liệu từ client
        ssize_t recv_len = recvfrom(sockfd, buffer, sizeof(buffer), 0, (struct sockaddr *)&client_addr, &client_len);
        if (recv_len < 0) {
            perror("Lỗi khi nhận dữ liệu");
            exit(1);
        }

        // Hiển thị thông điệp nhận được
        buffer[recv_len] = '\0';
        printf("Receive from client: %s\n", buffer);

        // Gửi phản hồi lại client
        if (sendto(sockfd, buffer, recv_len, 0, (struct sockaddr *)&client_addr, client_len) < 0) {
            perror("Lỗi khi gửi dữ liệu");
            exit(1);
        }
    }

    // Đóng socket
    close(sockfd);

    return 0;
}
