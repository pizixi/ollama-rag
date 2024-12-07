package main

import (
	"github.com/gin-gonic/gin"
	"embed"
	"io/fs"
	"flag"
	"log"
	"net/http"
)
//go:embed dashboard/*
var staticFiles embed.FS
func main() {
	gin.SetMode(gin.ReleaseMode)
    r := gin.New()
    fp, _ := fs.Sub(staticFiles, "dashboard")
    r.StaticFS("/", http.FS(fp))
	port := flag.String("p",":2356", "serve port")
	flag.Parse()
	log.Println(r.Run(*port))
}