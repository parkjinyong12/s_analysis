<template>
  <div class="sample-board">
    <h2>Sample 게시판</h2>
    <form class="sample-form" @submit.prevent="onSubmit">
      <input v-model="form.name" placeholder="이름" required />
      <input v-model="form.description" placeholder="설명" />
      <button type="submit">{{ form.id ? '수정' : '추가' }}</button>
      <button v-if="form.id" type="button" @click="resetForm">취소</button>
    </form>
    <table class="sample-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>이름</th>
          <th>설명</th>
          <th>생성일</th>
          <th>액션</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="sample in samples" :key="sample.id">
          <td>{{ sample.id }}</td>
          <td>{{ sample.name }}</td>
          <td>{{ sample.description }}</td>
          <td>{{ formatDate(sample.created_at) }}</td>
          <td>
            <button class="edit-btn" @click="editSample(sample)">수정</button>
            <button class="delete-btn" @click="deleteSample(sample.id)">삭제</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'SampleBoard',
  data() {
    return {
      samples: [],
      form: { id: null, name: '', description: '' },
      apiUrl: 'http://127.0.0.1:5000/samples',
    };
  },
  created() {
    this.fetchSamples();
  },
  methods: {
    async fetchSamples() {
      const res = await axios.get(this.apiUrl + '/');
      this.samples = res.data;
    },
    async onSubmit() {
      if (this.form.id) {
        // 수정
        await axios.put(`${this.apiUrl}/${this.form.id}`, {
          name: this.form.name,
          description: this.form.description,
        });
      } else {
        // 추가
        await axios.post(this.apiUrl + '/', {
          name: this.form.name,
          description: this.form.description,
        });
      }
      this.resetForm();
      this.fetchSamples();
    },
    editSample(sample) {
      this.form = { ...sample };
    },
    resetForm() {
      this.form = { id: null, name: '', description: '' };
    },
    async deleteSample(id) {
      if (confirm('정말 삭제하시겠습니까?')) {
        await axios.delete(`${this.apiUrl}/${id}`);
        this.fetchSamples();
      }
    },
    formatDate(val) {
      if (!val) return '';
      return new Date(val).toLocaleString();
    },
  },
};
</script>

<style scoped>
.sample-board {
  max-width: 700px;
  margin: 40px auto;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 16px rgba(0,0,0,0.08);
  padding: 32px 24px 24px 24px;
}
.sample-board h2 {
  margin-bottom: 24px;
  color: #1976d2;
}
.sample-form {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  flex-wrap: wrap;
  align-items: center;
}
.sample-form input {
  padding: 8px 12px;
  border: 1px solid #bdbdbd;
  border-radius: 6px;
  font-size: 15px;
  outline: none;
  transition: border 0.2s;
}
.sample-form input:focus {
  border: 1.5px solid #1976d2;
}
.sample-form button {
  padding: 8px 18px;
  border: none;
  border-radius: 6px;
  background: #1976d2;
  color: #fff;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s;
}
.sample-form button[type="button"] {
  background: #bdbdbd;
  color: #333;
}
.sample-form button:hover {
  background: #1565c0;
}
.sample-form button[type="button"]:hover {
  background: #757575;
  color: #fff;
}
.sample-table {
  width: 100%;
  border-collapse: collapse;
  background: #fafbfc;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.sample-table th, .sample-table td {
  padding: 12px 8px;
  text-align: center;
}
.sample-table th {
  background: #e3f2fd;
  color: #1976d2;
  font-weight: bold;
}
.sample-table tr {
  transition: background 0.2s;
}
.sample-table tr:hover {
  background: #f1f8ff;
}
.edit-btn {
  background: #43a047;
  color: #fff;
  margin-right: 6px;
}
.edit-btn:hover {
  background: #388e3c;
}
.delete-btn {
  background: #e53935;
  color: #fff;
}
.delete-btn:hover {
  background: #b71c1c;
}
</style> 