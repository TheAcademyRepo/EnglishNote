import {    
  ChevronRight,    
  Search,    
  House,    
  BarChart3,    
  Bell,    
  ChartPie,    
  Heart,    
  Wallet,    
  LogOut,    
  Moon,    
} from "lucide-react";    
export default function Topper(){
  return(
    <>
      <div className="glass rounded-xl m-6 p-6 bottom-5 z-[9999] fixed left-[35px] right-[35px] h-[75px]">
        
          <ul className="flex w-full h-full justify-between items-center">
            <li className="hover:bg-blue-200 hover:p-6"><House size={30}  /></li>
            <li><Bell size={30} /></li>
            <li><House size={30} /></li>
            <li><Search size={30} /></li>
          </ul>
        
      </div>
    </>
  );
}