<template>
    <div>

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
                    <div class="grab">
                        <div style="width: 200px; padding-left: 25px; padding-bottom: 5px">爬取的评论信息</div>
                        <el-input v-model="searchComment" style="width: 200px; padding-left: 25px" placeholder="请输入..."></el-input>
                        <el-button type="primary" @click="searchComments">搜索评论</el-button>
                         <el-table :data="comments" style="width: 100%">
                              <el-table-column prop="comment_text" label="评论内容" />
                              <el-table-column prop="flavor" label="口味" />
                              <el-table-column prop="environment" label="环境" />
                              <el-table-column prop="service" label="服务" />
                              <el-table-column prop="rating" label="评分" />
                              <el-table-column prop="user_id" label="用户ID" />
                              <el-table-column prop="shop_id" label="商店ID" />
                              <el-table-column prop="comment_date" label="评论日期" />
                              <el-table-column prop="sentiment_score" label="情感得分" />
                         </el-table>
                    </div>
                </el-card>
            </el-col>
        </el-row>
        <el-row :gutter="20" class="mgb20">
            <el-col :span="24">
                <el-card shadow="hover" body-class="card-body">
                    <div class="images">
                        <div v-for="image in images" :key="image" class="image-container">
                            <img :src="`/assets/img/${image}`" alt="Generated Image" />
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
const comments = ref([])

const  searchComment = ref()
const searchComments = async () => {
    try {
        const response = await request.get('/comments/api/comments', {
            params: { query: searchComment.value }
        });
        if (response.status === 200) {
            comments.value = response.data;
            ElMessage.success('搜索成功');
        } else {
            ElMessage.error('搜索失败');
        }
    } catch (error) {
        ElMessage.error('搜索失败');
    }
}



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
        const res = await request.post('/auth/api/run_script', param);

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
        const res = await request.post('/auth/api/run_analysis');

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

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  border: 1px solid #ddd;
  padding: 8px;
}

th {
  background-color: #f4f4f4;
}
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
