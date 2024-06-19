<template>
    <div>
        <el-row :gutter="20" class="mgb20">
            <el-col :span="6">
                <el-card shadow="hover" body-class="card-body">
                    <el-icon class="card-icon bg1">
                        <User />
                    </el-icon>
                    <div class="card-content">
                        <countup class="card-num color1" :end="6666" />
                        <div>用户访问量</div>
                    </div>
                </el-card>
            </el-col>
            <el-col :span="6">
                <el-card shadow="hover" body-class="card-body">
                    <el-icon class="card-icon bg2">
                        <ChatDotRound />
                    </el-icon>
                    <div class="card-content">
                        <countup class="card-num color2" :end="168" />
                        <div>系统消息</div>
                    </div>
                </el-card>
            </el-col>
            <el-col :span="6">
                <el-card shadow="hover" body-class="card-body">
                    <el-icon class="card-icon bg3">
                        <Goods />
                    </el-icon>
                    <div class="card-content">
                        <countup class="card-num color3" :end="8888" />
                        <div>商品数量</div>
                    </div>
                </el-card>
            </el-col>
            <el-col :span="6">
                <el-card shadow="hover" body-class="card-body">
                    <el-icon class="card-icon bg4">
                        <ShoppingCartFull />
                    </el-icon>
                    <div class="card-content">
                        <countup class="card-num color4" :end="568" />
                        <div>今日订单量</div>
                    </div>
                </el-card>
            </el-col>
        </el-row>
        <el-row :gutter="20" class="mgb20">
            <el-col :span="24">
                <el-card shadow="hover" body-class="card-body">
                    <div class="grab">
                        <div style="width: 200px; padding-left: 25px; padding-bottom: 5px">爬取应用数据</div>
                        <el-input v-model="grabId" style="width: 200px; padding-left: 25px" placeholder="请输入爬取应用id"></el-input>
                        <el-input v-model="grabNum" style="width: 200px; padding-left: 25px; padding-right: 25px;" placeholder="请输入爬取页数"></el-input>
                        <el-button type="primary" :icon="Search" @click="grabData()">点击爬取</el-button>
                        <el-button type="primary" @click="getImages">获取图片</el-button>
                    </div>
                </el-card>
            </el-col>
        </el-row>
        <el-row :gutter="20" class="mgb20">
            <el-col :span="24">
                <el-card shadow="hover" body-class="card-body">
                    <div class="images">
                        <div v-for="image in images" :key="image" class="image-container">
                            <img :src="`/api/get_image/${image}`" alt="Generated Image" />
                        </div>
                    </div>
                </el-card>
            </el-col>
        </el-row>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { ElMessage } from 'element-plus';
import request from '@/utils/request';
import { Search } from '@element-plus/icons-vue';
import countup from '@/components/countup.vue';

const grabNum = ref();
const grabId = ref();
const images = ref([]);

const grabData = async () => {
    if (!grabNum.value || !grabId.value) {
        ElMessage.error('请提供抓取的页数和应用ID');
        return;
    }

    const param = {
        grabNum: grabNum.value,
        grabId: grabId.value
    };

    try {
        const res = await request.post('/api/run_script', param);

        if (res.status === 200) {
            ElMessage.success('执行成功');
        } else {
            ElMessage.error('执行失败');
        }
    } catch (error) {
        ElMessage.error('执行失败');
    }
};

const getImages = async () => {
    try {
        const res = await request.post('/api/run_analysis');

        if (res.status === 200) {
            images.value = res.data.images;
            ElMessage.success('获取图片成功');
        } else {
            ElMessage.error('获取图片失败');
        }
    } catch (error) {
        ElMessage.error('获取图片失败');
    }
};
</script>

<style scoped>
.card-body {
    display: flex;
    align-items: center;
    height: 100px;
    padding: 0;
}

.card-content {
    flex: 1;
    text-align: center;
    font-size: 14px;
    color: #999;
    padding: 0 20px;
}

.card-num {
    font-size: 30px;
}

.card-icon {
    font-size: 50px;
    width: 100px;
    height: 100px;
    text-align: center;
    line-height: 100px;
    color: #fff;
}

.bg1 {
    background: #2d8cf0;
}

.bg2 {
    background: #64d572;
}

.bg3 {
    background: #f25e43;
}

.bg4 {
    background: #e9a745;
}

.color1 {
    color: #2d8cf0;
}

.color2 {
    color: #64d572;
}

.color3 {
    color: #f25e43;
}

.color4 {
    color: #e9a745;
}

.images {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    justify-content: center;
}

.image-container {
    width: 100%;
    text-align: center;
}

.image-container img {
    max-width: 100%;
    height: auto;
}
</style>
