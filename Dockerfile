FROM golang:1.22

WORKDIR /app

# Copia os arquivos do projeto
COPY go.mod .
COPY go.sum . 2>/dev/null || true
RUN go mod download

COPY . .

# Mantém o container em modo dev
CMD ["go", "run", "main.go"]
