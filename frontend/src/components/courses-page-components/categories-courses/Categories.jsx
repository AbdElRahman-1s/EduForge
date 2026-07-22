import { useState } from 'react';
import './categories.css';

const categories = [
  'All',
  'Development',
  'Data Science',
  'Design',
  'Business',
  'Marketing'
]

function Categories() {

  const [selectCategory, setSelectCategory] = useState("All");

  return (
    <section>
      <div className="contain">
        <div className="categories-div">
          {categories.map((category, i) => {
            return (
              <span
                key={i}
                className={selectCategory === category? "category-active" : "category"}
                onClick={() => {setSelectCategory(category)}}
              >{category}
              </span>
            )
          })}


        </div>



      </div>



    </section>
  )
}

export default Categories