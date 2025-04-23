<template>
      <div class="table-content">
        <table>
          <thead>
            <tr>
              <th>Key Maturity Area</th>
              <th>Assessed Level</th>
              <th>CHEK Benchmark</th>
              <th>IntelliCHEK Justification</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in mat_data" :key="index">
              <td>{{ item.label }}</td>
              <td>{{ item.level }}</td>
              <td>{{ item.benchmark }}</td>
              <td>{{ item.justification }}</td>
            </tr>
          </tbody>
        </table>
      </div>
  </template>
  
  <script setup> 
  const props = defineProps({
    mat_data: {
      type: Array,
      required: true,
    },
  });
  </script>
  
  <style scoped>

  /* .table-content {
    margin: 10px 0;
  }
  
  table {
    width: 100%;
    border-collapse: collapse;
  }
   */
  /* th, td {
    border: 1px solid #ddd;
    padding: 8px;
  }
  
  th {
    background-color: #f2f2f2;
    text-align: left;
  }
  
  tr:nth-child(even) {
    background-color: #f9f9f9;
  }
  
  tr:hover {
    background-color: #ddd;
  } */
  </style>
  