/* config.go */
/*
modification history
--------------------
Fei, create
*/
/*
DESCRIPTION
parse the spider.conf
*/

package config

import (
	"fmt"
	"path"
	"regexp"
)

import (
	"code.google.com/p/gcfg"
)

type SpiderConfig struct {
	UrlListFile     string
	OutputDirectory string
	MaxDepth        int
	CrawlInterval   int
	CrawlTimeout    int
	TargetUrl       string
	ThreadCount     int
}

type versionConfig struct {
	version string
}

const (
	DEFAULT_VERSION = "0.0"
)


/**
 * Description : 加载配置
 */
func LoadConfig(filePath string) (SpiderConfig, error) {
	var err error
	cfg := struct {
		Spider SpiderConfig
	}{}
	filePath = path.Join(filePath, "spider.conf")
	if err = gcfg.ReadFileInto(&cfg, filePath); err != nil {
		return SpiderConfig{}, err
	}
	if err = cfg.Spider.check(); err != nil {
		return SpiderConfig{}, err
	}
	return cfg.Spider, nil
}


/**
 * Description : 加载version配置
 */
func LoadVersion(filePath string) (versionConfig) {
	var err error
	cfg := struct {
		versionCfg versionConfig
	}{}
	filePath = path.Join(filePath, "version.conf")
	if err = gcfg.ReadFileInto(&cfg, filePath); err != nil {
		return DEFAULT_VERSION
	}
	return cfg.versionCfg.version
}

/**
 * Description: 确保配置项合法性
 */
func (c SpiderConfig) check() error {
	if c.MaxDepth < 0 {
		return fmt.Errorf("SpiderConfig.MaxDepth %d, must >= 0", c.MaxDepth)
	}
	if c.CrawlInterval <= 0 {
		return fmt.Errorf("SpiderConfig.CrawlInterval %d, must > 0", c.CrawlInterval)
	}
	if c.CrawlTimeout <= 0 {
		return fmt.Errorf("SpiderConfig.CrawlTimeout %d, must > 0", c.CrawlTimeout)
	}
	if c.ThreadCount <= 0 {
		return fmt.Errorf("SpiderConfig.ThreadCount %d, must > 0", c.ThreadCount)
	}
	if _, err := regexp.Compile(c.TargetUrl); err != nil {
		return fmt.Errorf("SpiderConfig.TargetUrl[%s] compile fails, %s", c.TargetUrl, err)
	}
	return nil
}
